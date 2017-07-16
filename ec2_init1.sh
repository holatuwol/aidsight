#!/bin/bash

sudo mkdir /mnt/github
sudo chown $USER:$USER /mnt/github

cd /mnt/github
git clone https://github.com/holatuwol/aidsight.git

sudo mkdir /mnt/docker
sudo ln -s /mnt/docker /var/lib/docker

sudo apt-get install -y docker docker.io

sudo service docker start
sudo usermod -aG docker $USER