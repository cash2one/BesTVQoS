#! /bin/bash

date=$1
hour=$2
b2b_type=$3

MAX_TRY=5
i=0

while(($i<$MAX_TRY))
do
	bash download_files_by_hour.sh ${date} ${hour} ${b2b_type}

	if [ -e TPLAYLOADING_*.zip ]
	then
		break
	fi

	i=$(($i+1))
	sleep 60	
done
