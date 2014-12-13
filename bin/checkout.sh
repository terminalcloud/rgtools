#!/bin/sh
cd ~/.rgtools
git pull --rebase
cd ~/.repository
git fetch
git checkout "$1"
