#! /usr/bin/bash

type=$1
svr=$2
date=$3
hour=$4
filename=$5

code_list=($(cat ${filename} | awk -F'|' '{print $2}'))

length=${#code_list[@]}

for ((i=0; i<$length; i++))
do
	code=${code_list[$i]}
	
	perl url_distribution_calc.pl ${type} ${svr} ${date} ${hour} url_${code} 0 tmp/${type}/${date}/${svr}/${code}_hour
	
	rm tmp/${type}/${date}/${svr}/${code}_hour
done