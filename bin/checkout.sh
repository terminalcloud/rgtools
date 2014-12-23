#!/bin/bash
cd ~/.rgtools
git fetch
git checkout origin/master
cd ~/.repository
git fetch
git checkout "$1"
