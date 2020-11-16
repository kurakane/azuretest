# 各種定義ファイル.

# AzureBatchのバッチアカウント名.
BATCH_ACCOUNT_NAME = 'yamayamabatch'
# AzureBatchのアクセスキー.
BATCH_ACCOUNT_KEY = 'Ko5u/RSuisLs/D4KnrS0m/DHzh07TaILWqw94kO4RXv6A2ylh2dtLOEmm6zVdr8OrCmVjsap7yTul4mKhpdeBw=='
# AzureBatchのアカウントURL
BATCH_ACCOUNT_URL = 'https://yamayamabatch.westus.batch.azure.com'

# AzureStrageのアカウント名.
STORAGE_ACCOUNT_NAME = 'yamayamastorage'
# AzureStrageのアクセスキー.
STORAGE_ACCOUNT_KEY = '7gYfZ5I+wqoFVBPNW3WiihawzUPmf2E6N/E7P4ggzFcU0Jt/OrvItof5UfpfJjr2TD7+n1smZcHfjwz7IwoEAA=='

# アップロード先のAzureStorageコンテナ名.
STORAGE_CONTAINER_UPLOAD = 'data-in'
# ダウンロード先のAzureStorageコンテナ名.
STORAGE_CONTAINER_DOWNLOAD = 'data-out'

# POOL ID.
POOL_ID = 'yamayamapool'
# JOB IDのプリフィックス.
JOB_ID_PREFIX = 'job_'
# Task約定データ検索.
TASK_ID_SELECT = 't_select'
# Task計算のプリフィックス.
TASK_ID_CACL_PREFIX = 't_calc_'
# Task集約.
TASK_ID_AGGR = 't_aggr'

# タイムアウト値(分)
TIMEOUT_SELECT = 3
TIMEOUT_CALC = 5
TIMEOUT_AGGR = 3

# Task約定データ検索のファイル名.
TASK_SELECT_APP = 'task_select.py'
# Task計算のファイル名.
TASK_CALC_APP = 'task_calc.py'
# Task集約のファイル名.
TASK_AGGR_APP = 'task_aggr.py'

# コンテナのURL.
CONTAINER_URL = 'yamayamaregistory.azurecr.io'
# Pythonのコンテナ名.
CONTAINER_PY_NAME = '/azurecloud:latest'
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

# POOL ID.
NEW_POOL_ID = 'yamayamapools'
# POOLのVMサイズ. Standard_A1_v2
NEW_POOL_VM_SIZE = 'Standard_A1_v2'
# POOLのノード数.
NEW_POOL_NODE_COUNT = 1
# Storage接続文字列
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=yamayamastorage;AccountKey=7gYfZ5I+wqoFVBPNW3WiihawzUPmf2E6N/E7P4ggzFcU0Jt/OrvItof5UfpfJjr2TD7+n1smZcHfjwz7IwoEAA==;EndpointSuffix=core.windows.net'