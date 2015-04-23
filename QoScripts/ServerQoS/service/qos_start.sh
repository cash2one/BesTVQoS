#! /usr/bin/env bash

export PYTHONPATH=/usr/bin/python:/usr/bin/python2.6:/usr/lib/python2.6/site-packages

date=$(date -d -1hour +"%Y%m%d")
#date=$1

hour=$(date -d -1hour +%H)
#hour=$2

bash server_qos_start.sh ${date} ${hour} B2C

