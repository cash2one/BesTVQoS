#! /usr/bin/bash

type=$1
svr=$2
servicetype=$3
date=$4
hour=$5
filename=$6

code_list=($(cat ${filename} | awk -F'|' '{print $2}'))

length=${#code_list[@]}

for ((i=0; i<$length; i++))
do
	code=${code_list[$i]}
	
	perl url_distribution_calc.pl ${type} ${svr} ${servicetype} ${date} ${hour} url_${code} 0 tmp/${type}/${date}/${servicetype}/${svr}/${code}_hour

	python update_data_into_db_by_code_date.py ${type} ${svr} ${servicetype} ${date} ${hour} ${code} ${type}/${date}/${servicetype}/${svr}/distribution_data_url_${code}_${hour}
	
	rm tmp/${type}/${date}/${servicetype}/${svr}/${code}_hour
done
