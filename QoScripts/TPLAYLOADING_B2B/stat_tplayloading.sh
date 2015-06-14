#! /bin/bash

#date=$(date -d "1day ago" +%Y%m%d)
date=$1
olddate=$(date -d "2day ago" +%Y%m%d)

B2B_TYPE=('ANHUIYD' 'FUJIANDX' 'JIANGSUYD')

for b2b_type in ${B2B_TYPE[@]}
do 
	filename="./data/${b2b_type}/${b2b_type}_${date}.csv"
	# 0. merge data from hourly data
	if [ -d ./data/${b2b_type}/${date} ]
	then
	    cat ./data/${b2b_type}/${date}/*.log > ${filename}
	fi

	mkdir -p "out/${b2b_type}/total"
	mkdir -p "out/${b2b_type}/${date}"
	# 1. stat versions and dist
	echo "stat versions"
	versions_file="out/${b2b_type}/${date}/versions_dist_24"
	perl stat_versions_dist.pl $date ${b2b_type} ${filename} ${versions_file}

	# 2. filter dbuffer by version, view type, loading type
	echo "filter dbuffer by version"
	mkdir -p "temp/${b2b_type}/${date}"
	perl filter_playloading_by_version_view_load.pl $date ${b2b_type} ${versions_file} ${filename}

	# 3. get pnvalues of dbuffer by version, view type, loading type
	echo "get pnvalues"
	pnvalues_file="out/${b2b_type}/${date}/pnvalues_${date}_24"
	if [ -f ${pnvalues_file} ]
	then
		rm -f ${pnvalues_file}
	fi

	for i in ./temp/${b2b_type}/${date}/*${date}24.log;
	do
		echo $i;
		perl get_pnvalues_by_version_view_load.pl ${date} ${b2b_type} $i ${pnvalues_file}
	done

	if [ -d ./data/${b2b_type}/${olddate} ]
	then
		rm -rf ./data/${b2b_type}/${olddate}
	fi

	if [ -d ./temp/${b2b_type}/${olddate} ]
	then
		rm -rf ./temp/${b2b_type}/${olddate}
	fi

#bash plot_daily_pnvalues.sh ${date}
done
echo "done...";
