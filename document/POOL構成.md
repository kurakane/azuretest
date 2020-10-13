# AzureBatch用のメモ

## POOLの作成
* プールの詳細
  * プール ID : kurakanepool
  * 表示名 : (入力しない)

* オペレーティング システム
  * イメージの種類 : Marketplace
  * 発行者 : microsoft-azure-batch
  * オファー : ubuntu-server-container
  * SKU : 16-04-lts (自動入力される)
  * Disk Encryption 構成 : None (変更しない)
  * データ ディスク : 0 (変更しない)
  * コンテナー構成 : カスタム 
    * コンテナーの種類 : 互換性のある Docker