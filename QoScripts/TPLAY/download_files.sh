#! usr/bin/bash

date=$1
hour=$2

MAX_TRY=5
i=0

while(($i<$MAX_TRY))
do
	bash download_files_by_FTP.sh ${date} ${hour}

	if [ -e TPLAY_${date}${hour}55_JSDX_.zip ]; then
		break
	fi

	i=$(($i+1))
	sleep 60	
done
