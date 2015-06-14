#! /bin/bash

date=$1
#date=$(date -d -1hour +"%Y%m%d")
hour=$2
#hour=$(date -d -1hour +%H)

mkdir -p "temp/${date}"
mkdir -p "data/${date}"
mkdir -p "out/total"
mkdir -p "out/${date}"

#1. download hourly files
bash download_files_with_5tries.sh $date $hour
bash unzip_log.sh $date

#2. filter hourly dbufer
echo "filter dbuffer by hour"
playtm_file="out/${date}/playtm_${date}_${hour}"
for i in ./data/${date}/*_${date}${hour}*.log;
do
	versions_file="out/${date}/versions_dist_${hour}"
	perl stat_versions_dist.pl $date $i ${versions_file}
	perl filter_playloading_by_hour.pl $date $hour ${versions_file} $i
	perl get_playtm.pl ${date} ${hour} $i ${playtm_file}
done

#3. get hourly pnvalues
echo "get pnvalues by hour"
pnvalues_file="out/${date}/pnvalues_${date}_${hour}"
if [ -f ${pnvalues_file} ]
then
	rm -f ${pnvalues_file}
fi

if [ -f ${playtm_file} ]
then
	rm -f ${playtm_file}
fi

for i in ./temp/${date}/*${date}${hour}.log;
do
	echo $i;
	perl get_pnvalues_by_hour.pl ${date} ${hour} $i ${pnvalues_file}
done

#4. done
echo "stat tplayloading by hour done..."
