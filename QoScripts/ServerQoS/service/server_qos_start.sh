#! /usr/bin/env bash

export PYTHONPATH=/usr/bin/python:/usr/bin/python2.6:/usr/lib/python2.6/site-packages

#date=$(date -d -1hour +"%Y%m%d")
date=$1 

#hour=$(date -d -1hour +%H)
hour=$2 

#bash prepare_for_qos.sh ${date} ${hour}

svr_type=('B2B' 'B2C')

for type in ${svr_type[@]}
do
	mkdir -p tmp/${type}/${date}
	mkdir -p ${type}/${date}
	
	perl filter_data_by_svrip.pl ${type} ${date} ${hour} svrip 1 log/${type}/${date}${hour}*.log

	bash server_qos_by_svrip.sh ${type} ${date} ${hour} ${type}/${date}/distribution_data_svrip_${hour}

	# clean the tmp data
	#rm log/${type}/${date}${hour}*.log

done
