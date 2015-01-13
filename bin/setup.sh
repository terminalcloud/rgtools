#!/bin/bash
cd /root
if [ -a .repository/Snapfile ]; then
    /root/.rgtools/bin/installsnap snap .repository/Snapfile
elif [ -a .repository/Dockerfile ]; then
    /root/.rgtools/bin/installdocker snap .repository/Dockerfile
fi
. /root/.bashrc
cat >> /CL/hooks/startup.sh << EOF
/srv/cloudlabs/scripts/send_message.sh CLIENTMESSAGE '{"id": "1","data": "source /root/.bashrc; history -c ;clear \n","type": "write_to_term","to": "computer"}';
EOF