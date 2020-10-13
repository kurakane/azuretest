# AzureBatchをクライアントから操作するモジュール.
# このモジュールはオンプレ側で実行され, AzureBatchを操作します.

import datetime
import sys

import azure.batch.batch_auth as batch_auth
import azure.batch.batch_service_client as batch
import azure.batch.models as batchmodels

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
    pass


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

    # 検索用のTASKを投入する.

    print('AzureBatchテスト用のクライアントを正常終了しました')


if __name__ == '__main__':
    run()
