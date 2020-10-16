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
JOB_ID_PREFIX = 'kurkanejob_'
# Task約定データ検索のプリフィックス.
TASK_ID_SELECT_PREFIX = 'task_select_trade_'
# Task計算のプリフィックス.
TASK_ID_CACL_PREFIX = 'task_calc_'

# Task約定データ検索のファイル名.
TASK_SELECT_APP = 'task_select.py'
# Task計算のファイル名.
TASK_CALC_APP = 'task_calc.py'

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
