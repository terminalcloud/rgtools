#!/bin/bash
cd ~/
if [ -a .repository/Snapfile ]; then
    /root/.rgtools/bin/runsnap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    /root/.rgtools/bin/rundocker snap .repository/Dockerfile
fi
