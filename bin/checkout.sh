#!/bin/bash
cd /root/.rgtools
git fetch
git checkout origin/master
cd /root/.repository
git fetch
git checkout "$1"
