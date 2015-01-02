#!/bin/bash
cd /root
if [ -a .repository/Snapfile ]; then
    installsnap snap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    installdocker snap .repository/Dockerfile
fi
. /root/.bashrc
