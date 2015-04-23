#! /usr/bin/env bash

export PYTHONPATH=/usr/bin/python:/usr/bin/python2.6:/usr/lib/python2.6/site-packages

#date=$(date -d -1hour +"%Y%m%d")
date=$1

bash server_qos_start_by_day.sh ${date} 24 B2B

