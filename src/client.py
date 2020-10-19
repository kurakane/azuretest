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
    if not client.pool.exists(cfg.POOL_ID) :
        raise RuntimeError(f'POOLが存在しません. 異常終了します. [{cfg.POOL_ID}]')

    # POOLのステータスチェックを行う.
    pool = client.pool.get(cfg.POOL_ID)
    if pool.state != batchmodels.PoolState.active:
        raise RuntimeError(f'POOLがActiveではありません. 異常終了します. [{cfg.POOL_ID}] [{pool.state}]')

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

    print(f'JOBを投入します. [{job_id}]')

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
        print(f'[{result.task_id}] [{result.status}]')
        if result.status != batchmodels.TaskAddStatus.success:
            raise RuntimeError("Taskの投入に失敗しました.")


def create_select_task(client, job_id):
    """約定データ検索用のタスクを投入する."""
    command = 'python ' + cfg.TASK_SELECT_APP

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_SELECT_PREFIX
    # TASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )

    print(f'TASK(約定データ検索)を投入します. [{task_id}]')

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

    # センシティビティのTASK_IDを決定する.
    for i in range(50):
        task_id = cfg.TASK_ID_CACL_PREFIX + str(i)
        task_ids.append(task_id)

        task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )
        tasks.append(task)

    print(f'TASK(計算)を投入します. [{task_ids}]')

    # TASKをJOBに追加する.
    result = client.task.add_collection(job_id, tasks)
    eval_task_status(result)

    print(f'TASK(計算)を投入しました. [{task_ids}]')

    return task_ids


def wait_for_tasks_to_complete(client, job_id, timeout):
    """タスクが完了するのを監視する."""
    timeout_expiration = datetime.datetime.now() + timeout

    sec = 1
    while datetime.datetime.now() < timeout_expiration:
        print(f'\rタスクの終了を監視しています. タイムアウト[{timeout}] [{datetime.timedelta(seconds=sec)}]', end='')
        sys.stdout.flush()

        # TASKの一覧を取得する.
        tasks = client.task.list(job_id)
        incomplete_tasks = [task for task in tasks if task.state != batchmodels.TaskState.completed]

        if not incomplete_tasks:
            print()
            return True
        else:
            sec += 1
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
    print(f'ファイルを圧縮します. [{blob_file_name}] [{(os.path.getsize(cfg.FILE_TMP) / 1024 / 1024):,.3f} MB]')
    with open(cfg.FILE_TMP, 'rb') as f:
        data = f.read()
        with open(blob_file_name, 'wb') as f2:
            f2.write(bz2.compress(data))
    print(f'ファイルを圧縮しました. [{blob_file_name}] [{(os.path.getsize(blob_file_name) / 1024 / 1024):,.3f} MB]')

    print(f'ファイルをアップロードします. [{blob_file_name}]')
    # 検索条件のファイルをアップロードする.
    # その際はフォルダ名をJOB IDにする.
    blob_service_client.create_blob_from_path(
        container_name=cfg.STORAGE_CONTAINER_UPLOAD,
        blob_name=os.path.join(job_id, blob_file_name + '.bz2'),
        file_path=blob_file_name)
    print(f'ファイルをアップロードが完了しました. [{blob_file_name}]')

    # アップロード後にローカルのファイルを削除する.
    os.remove(cfg.FILE_TMP)
    os.remove(blob_file_name)


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
        condition = dummy.ObsTradeQueryBuilder(10000, 100)
        # 検索条件をアップロードする.
        upload_to_blob(blob_service_client, job_id, cfg.FILE_SELECT, condition)

        # 約定データ検索用のTASKを投入する.
        task_id = create_select_task(client, job_id)

        # 約定データ検索用のTASKを監視する.
        wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=5))

        # 約定データ検索用のTASKの終了コードを取得する.
        task_select = client.task.get(job_id, task_id)
        print(f"TASK(約定データ検索)が終了しました. [{task_id}] [{task_select.execution_info.result}]")
        if task_select.execution_info.result != batchmodels.TaskExecutionResult.success:
            raise RuntimeError("TASK(約定データ検索)が失敗しました. 異常終了します.")

        # 計算用のTASKを投入する.
        task_ids = create_calc_tasks(client, job_id)

        # 計算用のTASKを監視する.
        wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=20))

        # 計算用のTASKの終了コードを取得する.
        for task_id in task_ids:
            task_calc = client.task.get(job_id, task_id)
            print(f"TAKS(計算)が終了しました. [{task_id}] [{task_calc.execution_info.result}]")
            if task_calc.execution_info.result != batchmodels.TaskExecutionResult.success:       
                raise RuntimeError("TASK(計算)が失敗しました. 異常終了します.")

    except Exception as e:
        # 動いているタスクを強制終了する. 実際にここが役に立つのはタイムアウト時のみの想定.
        print(f"例外が発生しました.")
        for task in client.task.list(job_id):
            if task.state == batchmodels.TaskState.running:
                print(f'タスクを強制終了します. [{task.id}] [{task.state}]')
                client.task.terminate(job_id, task.id)

        # ジョブを終了する.
        print(f'ジョブを強制終了します. [{job_id}]')
        client.job.terminate(job_id, terminate_reason='異常終了')

        # 例外は呼び出し元に投げる.
        raise e

    # JOBを正常終了する.
    client.job.terminate(job_id, terminate_reason='正常終了')

    # TODO: AzureStorageから不要なファイルを削除する.

    print('AzureBatchテスト用のクライアントを正常終了しました.')


if __name__ == '__main__':
    run()
