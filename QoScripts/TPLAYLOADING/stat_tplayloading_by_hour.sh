#! /bin/bash

#date=$1
date=$(date -d -1hour +"%Y%m%d")
#hour=$2
hour=$(date -d -1hour +%H)

SRV_TYPE=('OTT' 'ANHUIYD' 'FUJIANDX' 'JIANGSUYD')
#SRV_TYPE=('OTT')

for srv_type in ${SRV_TYPE[@]}
do 
	mkdir -p "temp/${srv_type}/${date}"
	mkdir -p "data/${srv_type}/${date}"
	mkdir -p "out/${srv_type}/total"
	mkdir -p "out/${srv_type}/${date}"

	#1. download hourly files
	bash download_files_with_5tries.sh $date $hour $srv_type
	bash unzip_log.sh $date $hour ${srv_type} "data/${srv_type}/${date}"

	#2. filter hourly dbufer
	echo "filter dbuffer by hour"
	versions_file="out/${srv_type}/${date}/versions_dist_${hour}"
	playtm_file="out/${srv_type}/${date}/playtm_${date}_${hour}"
	if [ -f ${playtm_file} ]
	then
		rm -f ${playtm_file}
	fi

	data_file="./data/${srv_type}/${date}/TPLAYLOADING_${date}${hour}_${srv_type}.log"
	if [ -f  ${data_file} ]
	then
		perl stat_versions_dist.pl $date ${srv_type} ${data_file} ${versions_file}
		perl filter_playloading_by_hour.pl $date $hour ${srv_type} ${versions_file} ${data_file}
		perl get_playtm.pl ${date} ${hour} ${srv_type} ${data_file} ${playtm_file}
	fi

	#3. get hourly pnvalues
	echo "get pnvalues by hour"
	pnvalues_file="out/${srv_type}/${date}/pnvalues_${date}_${hour}"
	if [ -f ${pnvalues_file} ]
	then
		rm -f ${pnvalues_file}
	fi
	for i in ./temp/${srv_type}/${date}/*${date}${hour}.log;
	do
		echo $i;
		perl get_pnvalues_by_hour.pl ${date} ${hour} ${srv_type} $i ${pnvalues_file}
	done
done
#4. done
echo "stat tplayloading by hour done..."
