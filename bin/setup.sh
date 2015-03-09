#!/bin/bash
cd /root
if [ -a .repository/snapfile ]; then
    /root/.rgtools/bin/installsnap .repository/snapfile
elif [ -a .repository/Snapfile ]; then
    /root/.rgtools/bin/installsnap  .repository/Snapfile
elif [ -a ./*_snapfile ]; then
    /root/.rgtools/bin/installsnap  ./*_snapfile
elif [ -a .repository/Dockerfile ]; then
    /root/.rgtools/bin/installdocker snap .repository/Dockerfile
elif [ -a .repository/DOCKERFILE ]; then
    /root/.rgtools/bin/installdocker snap .repository/DOCKERFILE
fi
. /root/.bashrc
cat >> /CL/hooks/startup.sh << EOF
/srv/cloudlabs/scripts/send_message.sh CLIENTMESSAGE '{"id": "1","data": "source /root/.bashrc; history -c ;clear \n","type": "write_to_term","to": "computer"}';
EOF