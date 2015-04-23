#! /usr/bin/bash

type=$1
date=$2
hour=$3
filename=$4

svr_list=($(cat ${filename} | awk -F'|' '{print $2}'))

length=${#svr_list[@]}

for ((i=0; i<$length; i++))
do
	svr=${svr_list[$i]}
	
	mkdir -p ${type}/${date}/${svr}
	mkdir -p tmp/${type}/${date}/${svr}
		
	# column 5 is response code, 1 is to write subfile
	perl key_distribution_calc.pl ${type} ${svr} ${date} ${hour} code 7 1 tmp/${type}/${date}/${svr}_hour
	
	# colume 4 is request url
	perl url_distribution_calc.pl ${type} ${svr} ${date} ${hour} url 0 tmp/${type}/${date}/${svr}_hour

	savedir=${type}/${date}/${svr}

	# response time
	perl calc_response_time_CDF.pl ${date} ${hour} 4 ${savedir} tmp/${type}/${date}/${svr}_hour

	# request time
	perl calc_response_time_CDF.pl ${date} ${hour} 5 ${savedir} tmp/${type}/${date}/${svr}_hour
	
	# calc qos by code	
	bash server_qos_by_code.sh ${type} ${svr} ${date} ${hour} ${type}/${date}/${svr}/distribution_data_code_${hour}

	#rm ${type}/${date}/${svr}/distribution_data_code_${hour}
	#rm ${type}/${date}/${svr}/distribution_data_url_${hour}
	
	# delete tmp files
	rm tmp/${type}/${date}/${svr}_hour
done
