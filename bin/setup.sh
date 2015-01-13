#!/bin/bash
cd /root
if [ -a .repository/Snapfile ]; then
    /root/.rgtools/bin/installsnap snap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    /root/.rgtools/bin/installdocker snap .repository/Dockerfile
fi
. /root/.bashrc
