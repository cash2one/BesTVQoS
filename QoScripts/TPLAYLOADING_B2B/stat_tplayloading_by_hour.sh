#! /bin/bash

date=$1
#date=$(date -d -1hour +"%Y%m%d")
hour=$2
#hour=$(date -d -1hour +%H)

B2B_TYPE=('ANHUIYD' 'FUJIANDX' 'JIANGSUYD')

for b2b_type in ${B2B_TYPE[@]}
do 
	mkdir -p "temp/${b2b_type}/${date}"
	mkdir -p "data/${b2b_type}/${date}"
	mkdir -p "out/${b2b_type}/total"
	mkdir -p "out/${b2b_type}/${date}"

	#1. download hourly files
	bash download_files_with_5tries.sh $date $hour $b2b_type
	bash unzip_log.sh $date $hour ${b2b_type} "data/${b2b_type}/${date}"

	#2. filter hourly dbufer
	echo "filter dbuffer by hour"
	for i in ./data/${b2b_type}/${date}/*_${date}${hour}*.log;
	do
		versions_file="out/${b2b_type}/${date}/versions_dist_${hour}"
		perl stat_versions_dist.pl $date ${b2b_type} $i ${versions_file}
		perl filter_playloading_by_hour.pl $date $hour ${b2b_type} ${versions_file} $i
	done

	#3. get hourly pnvalues
	echo "get pnvalues by hour"
	pnvalues_file="out/${b2b_type}/${date}/pnvalues_${date}_${hour}"
	if [ -f ${pnvalues_file} ]
	then
		rm -f ${pnvalues_file}
	fi

	for i in ./temp/${b2b_type}/${date}/*${date}${hour}.log;
	do
		echo $i;
		perl get_pnvalues_by_hour.pl ${date} ${hour} ${b2b_type} $i ${pnvalues_file}
	done
done
#4. done
echo "stat tplayloading by hour done..."
