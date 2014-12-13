#!/bin/sh
cd ~/
if [ -a .rgrepo/Snapfile ]; then
    installsnap .repository/Snapfile
elsif [ -a .rgrepo/Dockerfile ]; then
    installdocker snap .repository/Dockerfile
fi
. ~/.bashrc
