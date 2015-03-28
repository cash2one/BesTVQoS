#! /usr/bin/bash

date=$1
hour=$2

mkdir -p log

bash download_files.sh ${date} ${hour}

bash unzip_files.sh

perl filter_log_by_svrtype.pl log/TPLAY_${date}${hour}*.log

svr_type=('B2B' 'B2C')
for type in ${svr_type[@]}
do
	mkdir -p log/${type}
	mv log/TPLAY_${date}${hour}*_${type} log/${type}/
done

rm log/TPLAY_${date}${hour}*.log
