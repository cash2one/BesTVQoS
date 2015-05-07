#! usr/bin/bash

date=$1
hour=$2

ftp -n -v<<!
open 124.108.10.55
user ott_ts_tplay ott_ts_tplay
binary
prompt
mget TPLAY_${date}${hour}_JSDX_.zip
close
bye
!
