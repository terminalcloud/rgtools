#!/usr/bin/env bash

apt-get update || true
apt-get -y install python-pip python-dev git || yum -y install python-pip install python-dev git
pip install pyyaml

wget https://raw.githubusercontent.com/terminalcloud/rgtools/master/bin/reporun.py
chmod +x reporun.py
