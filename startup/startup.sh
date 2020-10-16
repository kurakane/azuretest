curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb

# これを実行しないとファイルがロックされていて落ちる. どれが悪さをしているかは不明.
sudo rm /var/lib/dpkg/lock
sudo rm /var/lib/dpkg/lock-frontend
# これを実行しないと blobfuseがインストールできないので追加.
sudo dpkg --configure -a

sudo dpkg -i packages-microsoft-prod.deb

# 先にゴミを削除しないと落ちるパターンあり.
# sudo rm -rf /var/lib/apt/lists/*
# sudo apt-get autoclean
# sudo apt-get clean

sudo apt-get update

# これを実行しないと blobfuseがインストールできないので追加.
sudo apt-get -f install

#sudo add-apt-repository main
#sudo add-apt-repository universe
#sudo add-apt-repository restricted

sudo apt-get install blobfuse

# ロックしているプロセスを見る
# ps aux | grep [a]pt

sudo mkdir /mnt/data-in
sudo mkdir /mnt/blobfusetmp-in -p
sudo blobfuse /mnt/data-in --tmp-path=/mnt/blobfusetmp-in --config-file=/mnt/batch/tasks/startup/wd/fuse_conn_in.cfg -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 -o allow_other

sudo mkdir /mnt/data-out
sudo mkdir /mnt/blobfusetmp-out -p
sudo blobfuse /mnt/data-out --tmp-path=/mnt/blobfusetmp-out --config-file=/mnt/batch/tasks/startup/wd/fuse_conn_out.cfg -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 -o allow_other
