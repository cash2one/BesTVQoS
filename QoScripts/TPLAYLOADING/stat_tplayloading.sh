#! /bin/bash

date=$(date -d "1day ago" +%Y%m%d)
#date=$1
olddate=$(date -d "2day ago" +%Y%m%d)

SRV_TYPE=('OTT' 'ANHUIYD' 'FUJIANDX' 'JIANGSUYD')
#SRV_TYPE=('OTT')

for srv_type in ${SRV_TYPE[@]}
do 
	mkdir -p "temp/${srv_type}/${date}"
	mkdir -p "out/${srv_type}/total"
	mkdir -p "out/${srv_type}/${date}"

	filename="./data/${srv_type}/${srv_type}_${date}.csv"
	# 1. merge data from hourly data
	if [ -d ./data/${srv_type}/${date} ]
	then
	    cat ./data/${srv_type}/${date}/*.log > ${filename}
	fi

	# 2. filter dbuffer by version, view type, loading type
	echo "filter dbuffer by version"
	versions_file="out/${srv_type}/${date}/versions_dist_24"
	playtm_file="out/${srv_type}/${date}/playtm_${date}_24"
	if [ -f ${playtm_file} ]
	then 
		rm -f ${playtm_file}
	fi

	if [ -f ${filename} ]
	then
		perl stat_versions_dist.pl $date ${srv_type} ${filename} ${versions_file}
		perl filter_playloading_by_version_view_load.pl $date ${srv_type} ${versions_file} ${filename}
		perl get_playtm.pl ${date} 24 ${srv_type} ${filename} ${playtm_file}
	fi

	# 3. get pnvalues of dbuffer by version, view type, loading type
	echo "get pnvalues"
	pnvalues_file="out/${srv_type}/${date}/pnvalues_${date}_24"
	if [ -f ${pnvalues_file} ]
	then
		rm -f ${pnvalues_file}
	fi
	for i in ./temp/${srv_type}/${date}/*${date}24.log;
	do
		echo $i;
		perl get_pnvalues_by_version_view_load.pl ${date} ${srv_type} $i ${pnvalues_file}
	done

	# 4. remove old files
	if [ -d ./data/${srv_type}/${olddate} ]
	then
		rm -rf ./data/${srv_type}/${olddate}
	fi

	if [ -d ./temp/${srv_type}/${olddate} ]
	then
		rm -rf ./temp/${srv_type}/${olddate}
	fi

#bash plot_daily_pnvalues.sh ${date}
done
echo "done...";
