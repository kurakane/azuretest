# AzureBatchをクライアントから操作するモジュール.
# このモジュールはオンプレ側で実行され, AzureBatchを操作します.
# memo : pip install azure-storage-blob

import bz2
import datetime
import os
import pickle
import sys
import time

import azure.batch.batch_auth as batch_auth
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels
import azure.storage.blob as azureblob

import cfg
import dummy


def create_batch_service_client():
    """AzureBatchの認証を行いBatchServiceClientを生成する."""
    # AzureBatchに対する認証を行う.
    credentials = batch_auth.SharedKeyCredentials(
        cfg.BATCH_ACCOUNT_NAME, cfg.BATCH_ACCOUNT_KEY)

    # batch_service_clientを生成する.
    return batch.BatchServiceClient(
        credentials, batch_url=cfg.BATCH_ACCOUNT_URL)


def check_pool(client, pool_id):
    """POOLの状態をチェックする."""
    # POOLの存在チェックを行う.
    if not client.pool.exists(pool_id) :
        raise RuntimeError(f'POOLが存在しません. 異常終了します. [{pool_id}]')

    # POOLのステータスチェックを行う.
    pool = client.pool.get(pool_id)
    if pool.state != batchmodels.PoolState.active:
        raise RuntimeError(f'POOLがActiveではありません. 異常終了します. [{pool_id}] [{pool.state}]')

    print(f'POOL STATE : [{pool_id}] [{pool.state}]')


def create_job(client, pool_id):
    """JOBを追加する."""

    # JOB IDを一意にするため時間を使う.
    start_time_for_job = "{0:%Y%m%d%H%M%S%f}".format(datetime.datetime.now())
    # JOB IDを決定する.
    job_id = cfg.JOB_ID_PREFIX + start_time_for_job

    # JOBを生成する.
    job = batch.models.JobAddParameter(
        id=job_id,
        pool_info=batch.models.PoolInformation(pool_id=pool_id))

    # JOBをPOOLに投入する.
    client.job.add(job)

    print(f'JOBを投入しました. [{job_id}]')
    return job_id


def setting_continer():
    """TaskContainerSettingsを生成する."""
    return batch.models.TaskContainerSettings(
        image_name=cfg.CONTAINER_URL + cfg.CONTAINER_PY_NAME,
        container_run_options=cfg.CONTAINER_PY_OPT)


def eval_task_status(task_return):
    """Taskの投入結果を判定する."""
    for result in task_return.value:
        # print(f'[{result.task_id}] [{result.status}]')
        if result.status != batchmodels.TaskAddStatus.success:
            raise RuntimeError("Taskの投入に失敗しました.")


def create_select_task(client, job_id):
    """約定データ検索用のタスクを投入する."""
    command = 'python ' + cfg.TASK_SELECT_APP

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_SELECT
    # TASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )

    # TASKをJOBに追加する.
    result = client.task.add_collection(job_id, [task])
    eval_task_status(result)

    print(f'TASK(約定データ検索)を投入しました. [{task_id}]')

    return task_id


def create_calc_tasks(client, job_id):
    """計算用のタスクを投入する"""
    """約定データ検索用のタスクを投入する."""
    command = 'python ' + cfg.TASK_CALC_APP

    task_ids = []
    tasks = []

    # ベースPVのTASK IDを決定する.
    task_id = cfg.TASK_ID_CACL_PREFIX + "BASE"
    task_ids.append(task_id)
    # ベースPVのTASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )
    tasks.append(task)

    for i in range(5):
        # センシティビティのTASK_IDを決定する.
        task_id = cfg.TASK_ID_CACL_PREFIX + str(i).zfill(3)
        task_ids.append(task_id)
        # センシティビティのTASKを生成する.
        task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )
        tasks.append(task)

    # TASKをJOBに追加する.
    result = client.task.add_collection(job_id, tasks)
    eval_task_status(result)

    print(f'TASK(計算)を投入しました. [{len(task_ids)}件]')

    return task_ids


def create_aggr_tasks(client, job_id, task_ids):
    """集約用のタスクを投入する."""
    command = 'python ' + cfg.TASK_AGGR_APP + ' ' + ' '.join(task_ids)

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_AGGR
    # TASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )

    # TASKをJOBに追加する.
    result = client.task.add_collection(job_id, [task])
    eval_task_status(result)

    print(f'TASK(集約)を投入しました. [{task_id}] ')

    return task_id


def wait_for_tasks_to_complete(client, job_id, timeout):
    """タスクが完了するのを監視する."""
    timeout_expiration = datetime.datetime.now() + timeout

    start_time = time.time()
    while datetime.datetime.now() < timeout_expiration:
        print(f'\rタスクを監視しています. タイムアウト[{timeout}] [{datetime.timedelta(seconds=int(time.time() - start_time))}]', end='')
        sys.stdout.flush()

        # TASKの一覧を取得する.
        tasks = client.task.list(job_id)
        incomplete_tasks = [task for task in tasks if task.state != batchmodels.TaskState.completed]

        if not incomplete_tasks:
            print(' 【完了】')
            return True
        else:
            time.sleep(1)

    print()
    print(f"Task監視がタイムアウトしました.")
    raise RuntimeError(f"Task監視がタイムアウトしました. [{timeout}]")


def upload_to_blob(blob_service_client, job_id, blob_file_name, obj):
    """指定されたファイルをAzureStorageにアップロードする."""
    # アップロードファイルをローカルに出力する.
    with open(cfg.FILE_TMP, 'wb') as f:
        pickle.dump(obj, f)

    # アップロードファイルをBZ2圧縮する.
    print(f'ファイルを圧縮します [{blob_file_name}]', end='')
    with open(cfg.FILE_TMP, 'rb') as f:
        data = f.read()
        with open(blob_file_name, 'wb') as f2:
            f2.write(bz2.compress(data))
    print(f' [{(os.path.getsize(cfg.FILE_TMP) / 1024 / 1024):,.3f} MB] to [{(os.path.getsize(blob_file_name) / 1024 / 1024):,.3f} MB] 【完了】')

    # 検索条件のファイルをアップロードする.
    # その際はフォルダ名をJOB IDにする.
    print(f'ファイルをアップロードします [{cfg.STORAGE_CONTAINER_UPLOAD}] [{blob_file_name}.bz2]', end='')
    blob_service_client.create_blob_from_path(
        container_name=cfg.STORAGE_CONTAINER_UPLOAD,
        blob_name=os.path.join(job_id, blob_file_name + '.bz2'),
        file_path=blob_file_name)
    print(f' 【完了】')

    # アップロード後にローカルのファイルを削除する.
    os.remove(cfg.FILE_TMP)
    os.remove(blob_file_name)


def is_task_failed(client, job_id):
    """全てのTASKが正常終了しているかを判定する."""
    return (client.job.get_task_counts(job_id).failed > 0)


def remove_input_file(blob_service_client, job_id, file_name):
    blob_name = os.path.join(job_id, file_name)
    if blob_service_client.exists(cfg.STORAGE_CONTAINER_UPLOAD, blob_name):
        print(f'入力ファイルを削除します. [{cfg.STORAGE_CONTAINER_UPLOAD}] [{blob_name}]', end='')
        blob_service_client.delete_blob(
            container_name=cfg.STORAGE_CONTAINER_UPLOAD,
            blob_name=blob_name
        )
        print(' 【完了】')


def remove_output_file(blob_service_client, job_id, task_ids):
    """npvファイルを全て削除する."""
    pass


def remove_input_files(blob_service_client, job_id):
    """JOBに紐付く入力ファイルを全て削除する. 1つ1つしか消せない."""

    # 検索条件を削除する.
    remove_input_file(blob_service_client, job_id, cfg.FILE_SELECT + '.bz2')
    # 休日情報を削除する.
    remove_input_file(blob_service_client, job_id, cfg.FILE_HOLIDAYS + '.bz2')
    # 約定データを削除する.
    remove_input_file(blob_service_client, job_id, cfg.FILE_TRADES + '.bz2')

    print("入力ファイルを全て削除しました.")


def run():
    """主処理."""
    print('AzureBatchテスト用のクライアントを起動しました')

    # AzureBatchアクセス用のクライアントを生成する.
    client = create_batch_service_client()

    # POOLの状態をチェックする.
    # POOLが使用できる状態でない場合は終了する.
    check_pool(client, cfg.POOL_ID)

    # JOBを投入する.
    job_id = create_job(client, cfg.POOL_ID)

    try:
        # AzureStorageのクライアントを生成する.
        blob_service_client = azureblob.BlockBlobService(
            account_name=cfg.STORAGE_ACCOUNT_NAME, account_key=cfg.STORAGE_ACCOUNT_KEY)

        # ★ダミーの休日情報を取得する.
        holidays = dummy.Holidays()
        # 休日情報をアップロードする.
        upload_to_blob(blob_service_client, job_id, cfg.FILE_HOLIDAYS, holidays)

        # ★ダミーの検索条件をシリアライズする.
        condition = dummy.ObsTradeQueryBuilder(5, 10)
        # 検索条件をアップロードする.
        upload_to_blob(blob_service_client, job_id, cfg.FILE_SELECT, condition)

        # 約定データ検索用のTASKを投入する.
        create_select_task(client, job_id)
        # 約定データ検索用のTASKを監視する.
        wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=cfg.TIMEOUT_SELECT))
        if is_task_failed(client, job_id):
            raise RuntimeError("TASK(約定データ検索)が失敗しました. 異常終了します.")

        # 計算用のTASKを投入する.
        task_ids = create_calc_tasks(client, job_id)
        # 計算用のTASKを監視する.
        wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=cfg.TIMEOUT_CALC))
        if is_task_failed(client, job_id):   
            raise RuntimeError("TASK(計算)が失敗しました. 異常終了します.")

        # 集約のTASKを投入する.
        create_aggr_tasks(client, job_id, task_ids)
        # 集約のTASKを監視する.
        wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=cfg.TIMEOUT_AGGR))
        if is_task_failed(client, job_id):
            raise RuntimeError("TASK(集約)が失敗しました. 異常終了します.")

    except Exception as e:
        # 動いているタスクを強制終了する. 実際にここが役に立つのはタイムアウト時のみの想定.
        print(f"例外が発生しました.")
        for task in client.task.list(job_id):
            if task.state in (batchmodels.TaskState.running, batchmodels.TaskState.active):
                print(f'タスクを強制終了します. [{task.id}] [{task.state}]')
                client.task.terminate(job_id, task.id)

        # ジョブを終了する.
        print(f'ジョブを強制終了します. [{job_id}]')
        client.job.terminate(job_id, terminate_reason='異常終了')

        # AzureStorageから入力ファイルを削除する.
        remove_input_files(blob_service_client, job_id)

        # 例外は呼び出し元に投げる.
        raise e

    # JOBを正常終了する.
    client.job.terminate(job_id, terminate_reason='正常終了')

    # AzureStorageから入力ファイルを削除する.
    remove_input_files(blob_service_client, job_id)
    # AzureStorageから出力ファイルを削除する
    remove_output_file(blob_service_client, job_id, task_ids)

    print('AzureBatchテスト用のクライアントを正常終了しました.')


if __name__ == '__main__':
    run()
