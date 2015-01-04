#!/bin/bash
cd ~/
if [ -a .repository/Snapfile ]; then
    runsnap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    rundocker snap .repository/Dockerfile
fi
