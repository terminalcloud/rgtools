#!/bin/sh
cd ~/
if [ -a .rgrepo/Snapfile ]; then
    installsnapfile .rgrepo/Snapfile
elsif [ -a .rgrepo/Dockerfile ]; then
    installdocker chroot .rgrepo/Dockerfile
fi
. ~/.bashrc
