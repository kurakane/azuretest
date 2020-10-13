# AzureBatch用のメモ POOL作成

## POOLの作成
* プールの詳細
  * プール ID : kurakanepool
  * 表示名 : (任意 入力しない)

* オペレーティング システム
  * イメージの種類 : Marketplace
  * 発行者 : microsoft-azure-batch
  * オファー : ubuntu-server-container
  * SKU : 16-04-lts (自動入力される)
  * Disk Encryption 構成 : None (変更しない)
  * データ ディスク : (変更しない)
  * コンテナー構成 : カスタム
    * コンテナーの種類 : 互換性のある Docker
    * コンテナー イメージ名 : kurakanecontainer.azurecr.io/azurecloud:test
    * コンテナレジストリーAZ_BATCH_JOB_ID
      * レジストリのユーザー名 : kurakanecontainer
      * パスワード : M61ttBIj+yYgzTiuzJGp=A77EDL4dxkv
      * レジストリ サーバー : kurakanecontainer.azurecr.io
* グラフィックスとレンダリングのライセンス
  * レンダリング用の測定ライセンス : (変更しない)
* ノード サイズ
  * VMサイズ : (変更しない)
* スケーリング
  * モード : 固定 (変更しない)
  * ターゲットの専用ノード数 : 1 (後からリサイズ可能)
  * ターゲットの低優先度ノード : 0 (後からリサイズ可能)
  * サイズ変更のタイムアウト : 15 (変更しない)
* 開始タスク
  * 開始タスク : 無効 (後から変更可能)

以下の構成は変更不要。  

まずはコンテナを設定した状態でNodeが正常に起動するのかを試した方がよい。  
