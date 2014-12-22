#!/bin/bash
cd ~/
if [ -a .rgrepo/Snapfile ]; then
    runsnap .repository/Snapfile
elif [ -a .rgrepo/Dockerfile ]; then
    rundocker snap .repository/Dockerfile
fi
