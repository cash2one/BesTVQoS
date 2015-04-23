#! usr/bin/bash

date=$1
hour=$2

ftp -n -v<<!
open 10.100.12.8
user bestvqos funshion
binary
cd /log/B2C/service/${date}
prompt
mget ${date}${hour}*.zip
close
bye
!
