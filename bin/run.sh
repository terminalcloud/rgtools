#!/bin/sh
cd ~/
if [ -a .rgrepo/Snapfile ]; then
    runsnapfile .rgrepo/Snapfile
elsif [ -a .rgrepo/Dockerfile ]; then
    rundocker chroot .rgrepo/Dockerfile
fi
