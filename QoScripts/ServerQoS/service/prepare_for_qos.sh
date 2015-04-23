#! /usr/bin/bash

type=$1
date=$2
hour=$3

mkdir -p log

bash download_files.sh ${date} ${hour}

bash unzip_files.sh

mkdir -p log/${type}
	
mv log/${date}${hour}*.log log/${type}/
