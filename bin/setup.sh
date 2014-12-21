#!/bin/bash
cd ~/
if [ -a .repository/Snapfile ]; then
    installsnap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    installdocker snap .repository/Dockerfile
fi
. ~/.bashrc
