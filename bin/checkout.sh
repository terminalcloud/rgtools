#!/bin/sh
cd ~/.rgtools
git pull --rebase
cd ~/.rgrepo
git fetch
git checkout "$1"
