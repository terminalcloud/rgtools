#!/bin/bash
echo "source /root/.bashrc; checkout.sh $1; setup.sh" | /srv/cloudlabs/scripts/run_in_term.js
