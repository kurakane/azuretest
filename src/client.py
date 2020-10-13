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
        print(f'POOLが存在しません. 異常終了します. [{cfg.POOL_ID}]')
        return False

    # POOLのステータスチェックを行う.
    pool = client.pool.get(cfg.POOL_ID)
    if pool.state != batchmodels.PoolState.active:
        print(f'POOLがActiveではありません. 異常終了します. [{cfg.POOL_ID}] [{pool.state}]')
        return False

    print(f'POOL STATE : {pool.state}')
    return True


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


def create_select_task(client, job_id):
    """約定データ検索用のタスクを投入する."""
    command = "python " + cfg.TASK_SELECT_APP

    # コンテナの設定を行う.
    task_container_setting = batch.models.TaskContainerSettings(
        image_name=cfg.CONTAINER_URL + cfg.CONTAINER_PY_NAME,
        container_run_options='--workdir /app')

    # TASK IDを決定する.
    task_id = cfg.TASK_ID_SELECT_PREFIX + job_id
    # TASKを生成する.
    task = batch.models.TaskAddParameter(
            id=task_id,
            command_line=command,
            container_settings=task_container_setting
            )

    print(f'TASK(約定データ検索)を投入します. [{task_id}]')

    # TASKをJOBに追加する.
    client.task.add_collection(job_id, [task])

    print(f'TASK(約定データ検索)を投入しました. [{task_id}]')


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
    raise RuntimeError("タイムアウトしました " + str(timeout))


def run():
    """主処理."""
    print('AzureBatchテスト用のクライアントを起動しました')

    # AzureBatchアクセス用のクライアントを生成する.
    client = create_batch_service_client()

    # POOLの状態をチェックする.
    if not check_pool(client, cfg.POOL_ID) :
        sys.exit(-1)

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

    # 検索用のTASKを投入する.
    create_select_task(client, job_id)

    # 検索用のTASKを監視する.
    wait_for_tasks_to_complete(client, job_id, datetime.timedelta(minutes=5))

    print('AzureBatchテスト用のクライアントを正常終了しました')


if __name__ == '__main__':
    run()
