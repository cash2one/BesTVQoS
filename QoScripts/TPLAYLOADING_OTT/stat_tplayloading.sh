#! /bin/bash

#date=$(date -d "1day ago" +%Y%m%d)
date=$1
filename="./data/ott_${date}.csv"
olddate=$(date -d "2day ago" +%Y%m%d)

# 0. merge data from hourly data
if [ -d ./data/${date} ]
then
    cat ./data/${date}/*.log > ${filename}
fi

mkdir -p "out/total"
mkdir -p "out/${date}"
# 1. stat versions and dist
echo "stat versions"
versions_file="out/${date}/versions_dist_24"
perl stat_versions_dist.pl $date ${filename} ${versions_file}

# 2. filter dbuffer by version, view type, loading type
echo "filter dbuffer by version"
mkdir -p temp/${date}
playtm_file="out/${date}/playtm_${date}_24"
if [ -f ${playtm_file} ]
then 
	rm -f ${playtm_file}
fi
perl filter_playloading_by_version_view_load.pl $date ${versions_file} ${filename}
perl get_playtm.pl ${date} 24 ${filename} ${playtm_file}

# 3. get pnvalues of dbuffer by version, view type, loading type
echo "get pnvalues"
pnvalues_file="out/${date}/pnvalues_${date}_24"
if [ -f ${pnvalues_file} ]
then
	rm -f ${pnvalues_file}
fi

for i in ./temp/${date}/*${date}24.log;
do
	echo $i;
	perl get_pnvalues_by_version_view_load.pl ${date} $i ${pnvalues_file}
done

# 4. remove old files
if [ -d ./data/${olddate} ]
then
	rm -rf ./data/${olddate}
fi

if [ -d ./temp/${olddate} ]
then
	rm -rf ./temp/${olddate}
fi

#bash plot_daily_pnvalues.sh ${date}

echo "done...";
