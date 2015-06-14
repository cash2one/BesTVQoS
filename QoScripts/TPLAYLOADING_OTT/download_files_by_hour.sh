#! /bin/bash

date=$1
hour=$2
echo "downloading file: date: ${date}, ${hour}"
ftp -n -v<<!
open 124.108.10.62
user ott_ts_tplayloading ott_ts_tplayloading
binary
prompt
mget TPLAYLOADING_${date}${hour}*_OTT.zip
close
bye
!
