#! /bin/bash

date=$1
hour=$2
b2b_type=$3

echo "downloading file: date: ${date}, ${hour}, ${b2b_type}"
ftp -n -v<<!
open 124.108.10.62
user ott_ts_tplayloading ott_ts_tplayloading
binary
prompt
mget TPLAYLOADING_${date}${hour}*_${b2b_type}.zip
close
bye
!
