# 各種定義ファイル.

# AzureBatchのバッチアカウント名.
BATCH_ACCOUNT_NAME = 'kurakane'
# AzureBatchのアクセスキー.
BATCH_ACCOUNT_KEY = 'KtuabRR1tPPPduMqLjMnuANzs4Uo0HOWZ0kRgy3ehvvvXR1AOtFWyy+iXPEv0br0PaH79ZUQClu9n8XFBYJYKA=='
# AzureBatchのアカウントURL
BATCH_ACCOUNT_URL = 'https://kurakane.japaneast.batch.azure.com'

# AzureStrageのアカウント名.
STORAGE_ACCOUNT_NAME = 'kurakanestrage'
# AzureStrageのアクセスキー.
STORAGE_ACCOUNT_KEY = 'vuMEUJwlfdHxnFsaCTMgW/zedeZA+k5do519n8OXE9QUW+J6aYQvHuoYvi5q/7aH7ylEEIixinWUEQObQH+WlQ=='

# アップロード先のAzureStorageコンテナ名.
STORAGE_CONTAINER_UPLOAD = 'data-in'
# ダウンロード先のAzureStorageコンテナ名.
STORAGE_CONTAINER_DOWNLOAD = 'data-out'

# POOL ID.
POOL_ID = 'kurakanepool'
# JOB IDのプリフィックス.
JOB_ID_PREFIX = 'job_'
# Task約定データ検索.
TASK_ID_SELECT = 't_select'
# Task計算のプリフィックス.
TASK_ID_CACL_PREFIX = 't_calc_'
# Task集約.
TASK_ID_AGGR = 't_aggr'

# タイムアウト値(分)
TIMEOUT_SELECT = 5
TIMEOUT_CALC = 1
TIMEOUT_AGGR = 10

# Task約定データ検索のファイル名.
TASK_SELECT_APP = 'task_select.py'
# Task計算のファイル名.
TASK_CALC_APP = 'task_calc.py'
# Task集約のファイル名.
TASK_AGGR_APP = 'task_aggr.py'

# コンテナのURL.
CONTAINER_URL = 'kurakanecontainer.azurecr.io'
# Pythonのコンテナ名.
CONTAINER_PY_NAME = '/azurecloud:test'
# Pythonコンテナ接続時のオプション.
CONTAINER_PY_OPT = '--workdir /app --volume /mnt/data-in:/' + STORAGE_CONTAINER_UPLOAD + ' --volume /mnt/data-out:/' + STORAGE_CONTAINER_DOWNLOAD

# アップロード時のローカルファイルのファイル名.
FILE_TMP = 'tmp.dmp'
# アップロードする休日情報のファイル名.
FILE_HOLIDAYS = 'Holidays'
# アップロードする検索条件のファイル名.
FILE_SELECT = 'ObsTradeQueryBuilder'
# 明細のファイル名.
FILE_TRADES = 'SplTrades'
