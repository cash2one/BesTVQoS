#! /usr/bin/bash

type=$1
date=$2
hour=$3
filename=$4

svr_list=($(cat ${filename} | awk -F'|' '{print $2}'))
type_list=($(cat ${filename} | awk -F'|' '{print $3}'))

length=${#svr_list[@]}

for ((i=0; i<$length; i++))
do
	svr=${svr_list[$i]}
    servicetype=${type_list[$i]}
	
	mkdir -p ${type}/${date}/${servicetype}/${svr}
	mkdir -p tmp/${type}/${date}/${servicetype}/${svr}
		
	# column 5 is response code, 1 is to write subfile
	perl key_distribution_calc.pl ${type} ${svr} ${servicetype} ${date} ${hour} code 7 1 tmp/${type}/${date}/${servicetype}/${svr}_hour
	
	# colume 4 is request url
	perl url_distribution_calc.pl ${type} ${svr} ${servicetype} ${date} ${hour} url 0 tmp/${type}/${date}/${servicetype}/${svr}_hour

	savedir=${type}/${date}/${servicetype}/${svr}

	# response time
	perl calc_response_time_CDF.pl ${date} ${hour} 4 ${savedir} tmp/${type}/${date}/${servicetype}/${svr}_hour
	perl calc_response_time_CDF_by_url.pl ${date} ${hour} 4 ${savedir} tmp/${type}/${date}/${servicetype}/${svr}_hour	

	# request time
	perl calc_response_time_CDF.pl ${date} ${hour} 5 ${savedir} tmp/${type}/${date}/${servicetype}/${svr}_hour
	perl calc_response_time_CDF_by_url.pl ${date} ${hour} 5 ${savedir} tmp/${type}/${date}/${servicetype}/${svr}_hour

	python update_data_into_db_date.py ${type} ${svr} ${servicetype} ${date} ${hour} ${type}/${date}/${servicetype}/${svr}/response_data_CDF_5 ${type}/${date}/${servicetype}/${svr}/response_data_CDF_4 ${type}/${date}/${servicetype}/${svr}/distribution_data_code_${hour}
	
	# calc qos by code	
	bash server_qos_by_code.sh ${type} ${svr} ${servicetype} ${date} ${hour} ${type}/${date}/${servicetype}/${svr}/distribution_data_code_${hour}

	#rm ${type}/${date}/${servicetype}/${svr}/distribution_data_code_${hour}
	#rm ${type}/${date}/${servicetype}/${svr}/distribution_data_url_${hour}
	
	# delete tmp files
	rm tmp/${type}/${date}/${servicetype}/${svr}_hour
done
