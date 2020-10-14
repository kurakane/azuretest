# AzureBatchをクライアントから操作するモジュール.
# このモジュールはオンプレ側で実行され, AzureBatchを操作します.
# memo : pip install azure-storage-blob

import datetime
import sys
import time
import os
import pickle

import azure.batch.batch_auth as batch_auth
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels
import azure.storage.blob as azureblob

import cfg


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
    return batch.models.TaskContainerSettings(
        image_name=cfg.CONTAINER_URL + cfg.CONTAINER_PY_NAME,
        container_run_options=cfg.CONTAINER_PY_OPT)


def eval_task_status(task_return):
    """Taskの投入結果を判定する."""
    # TODO 複数件チェック
    print(f"ステータス [{task_return.value[0].status}]")
    if task_return.value[0].status != batchmodels.TaskAddStatus.success:
        raise RuntimeError("Taskの投入に失敗しました")


def create_select_task(client, job_id):
    """約定データ検索用のタスクを投入する."""
    command = 'python ' + cfg.TASK_SELECT_APP

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_SELECT_PREFIX + job_id
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

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_CACL_PREFIX + job_id
    # TASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=setting_continer()
            )

    print(f'TASK(計算)を投入します. [{task_id}]')

    # TASKをJOBに追加する.
    resut = client.task.add_collection(job_id, [task])
    eval_task_status(resut)

    print(f'TASK(計算)を投入しました. [{task_id}]')


def wait_for_tasks_to_complete(client, job_id, timeout):
    """タスクが完了するのを監視する."""
    timeout_expiration = datetime.datetime.now() + timeout

    print(f'タスクの終了を監視しています. タイムアウト[{timeout}]', end='')
    while datetime.datetime.now() < timeout_expiration:
        print('.', end='')
        sys.stdout.flush()

        # TASKの一覧を取得する.
        tasks = client.task.list(job_id)
        incomplete_tasks = [task for task in tasks if task.state != batchmodels.TaskState.completed]

        if not incomplete_tasks:
            print()
            return True
        else:
            time.sleep(1)

    print()
    raise RuntimeError("Task監視がタイムアウトしました. [{timeout}]")


def run():
    """主処理."""
    print('AzureBatchテスト用のクライアントを起動しました')

    # AzureBatchアクセス用のクライアントを生成する.
    client = create_batch_service_client()

    # POOLの状態をチェックする.
    check_pool(client, cfg.POOL_ID)

    # JOBを投入する.
    job_id = create_job(client, cfg.POOL_ID)

    # AzureStorageのクライアントを生成する.
    blob_service_client = azureblob.BlockBlobService(
        account_name=cfg.STORAGE_ACCOUNT_NAME, account_key=cfg.STORAGE_ACCOUNT_KEY)

    # 検索条件をシリアライズする.
    condition = {'BOOK': 'T_CORE'}

    # 検索条件のファイルをローカルに生成する.
    with open(cfg.FILE_SELECT, 'wb') as f:
        pickle.dump(condition, f)

    # 検索条件のファイルをアップロードする.
    # その際はフォルダ名をJOB IDにする.
    blob_service_client.create_blob_from_path(
        container_name=cfg.STORAGE_CONTAINER_UPLOAD,
        blob_name=os.path.join(job_id, cfg.FILE_SELECT),
        file_path=cfg.FILE_SELECT)

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
    create_calc_tasks(client, job_id)

    # 計算用のTASKを監視する.
    wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=20))

    print('AzureBatchテスト用のクライアントを正常終了しました.')

if __name__ == '__main__':
    run()
