#!/bin/bash
cd ~/
service apache2 start
if [ -a .repository/Snapfile ]; then
    installsnap < /dev/null > /var/www/html/output.stdout 2> /var/www/html/output.stderr snap .repository/Snapfile
    echo $? > /var/www/html/output.exitCode
elif [ -a .repository/Dockerfile ]; then
    installdocker < /dev/null > /var/www/html/output.stdout 2> /var/www/html/output.stderr snap .repository/Dockerfile
    echo $? > /var/www/html/output.exitCode
fi
. ~/.bashrc
