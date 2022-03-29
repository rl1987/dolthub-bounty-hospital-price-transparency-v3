#!/bin/bash

apt-get update
apt-get install -y python3 python3-pip tmux git vim visidata
curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh > /tmp/install.sh && bash /tmp/install.sh
dolt config --global --add user.email rimantas@keyspace.lt
dolt config --global --add user.name "rl1987"
pip3 install openpyxl requests lxml js2xml doltpy xlrd

curl -sSL https://repos.insights.digitalocean.com/install.sh -o /tmp/install.sh
bash /tmp/install.sh
