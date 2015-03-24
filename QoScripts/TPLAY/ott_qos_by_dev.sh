#! /usr/bin/bash

svrtype=$1
date=$2
hour=$3
filename=$4

dev_list=($(cat ${filename} | awk -F'|' '{print $2}'))

length=${#dev_list[@]}

for ((i=0; i<$length; i++))
do
	echo ${dev_list[$i]}
	
	bash ott_qos.sh ${svrtype} ${date} ${hour} ${dev_list[$i]} tmp/${date}/${dev_list[$i]}_hour
	
	# delete tmp files
	rm tmp/${date}/${dev_list[$i]}_hour
done
