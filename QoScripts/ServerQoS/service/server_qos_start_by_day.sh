#! /usr/bin/env bash

date=$1 
hour=$2 
type=$3

mkdir -p tmp/${type}/${date}
mkdir -p ${type}/${date}
	
perl filter_data_by_svrip.pl ${type} ${date} ${hour} svrip 1 tmp/${type}/${date}/*_all

bash server_qos_by_svrip.sh ${type} ${date} ${hour} ${type}/${date}/distribution_data_svrip_${hour}

