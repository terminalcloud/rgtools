#!/bin/sh
cd ~/
if [ -a .rgrepo/Snapfile ]; then
    runsnap .repository/Snapfile
elsif [ -a .rgrepo/Dockerfile ]; then
    rundocker snap .repository/Dockerfile
fi
