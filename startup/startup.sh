wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb

# これを実行しないとファイルがロックされていて落ちる. どれが悪さをしているかは不明.
sudo rm /var/lib/dpkg/lock
# これを実行しないと blobfuseがインストールできないので追加.
sudo dpkg --configure -a

sudo dpkg -i packages-microsoft-prod.deb

sudo apt-get update

# これを実行しないと blobfuseがインストールできないので追加.
sudo apt-get -f install

sudo apt-get install blobfuse

sudo mkdir /mnt/data-in
sudo mkdir /mnt/blobfusetmp-in -p
sudo blobfuse /mnt/data-in --tmp-path=/mnt/blobfusetmp-in --config-file=/mnt/batch/tasks/startup/wd/fuse_conn_in.cfg -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 -o allow_other

sudo mkdir /mnt/data-out
sudo mkdir /mnt/blobfusetmp-out -p
sudo blobfuse /mnt/data-out --tmp-path=/mnt/blobfusetmp-out --config-file=/mnt/batch/tasks/startup/wd/fuse_conn_out.cfg -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 -o allow_other
