#! /usr/bin/bash

svrtype=$1
date=$2
hour=$3
dev=$4
filename=$5

savedir=${svrtype}/${date}/${dev}
mkdir -p ${savedir}

# playtype: 1-vod; 2-huikan; 3-live; 4-liankan; ''-unknow
pt=(1 2 3 4)

for playtype in ${pt[@]}
do
	perl fbuffer_cdf_by_hour.pl ${date} ${hour} ${playtype} ${savedir} ${filename}
	
	perl pchoke_ratio_by_hour.pl ${date} ${hour} ${playtype} ${savedir} ${filename}
	
	if [ ${hour} -eq 24 ]; then	
		perl playtime_by_usr.pl ${date} ${playtype} ${savedir} ${filename}
	fi
done

# for '' - unknown
perl fbuffer_cdf_by_hour.pl ${date} ${hour} '' ${savedir} ${filename}

perl pchoke_ratio_by_hour.pl ${date} ${hour} '' ${savedir} ${filename}

if [ ${hour} -eq 24 ]; then
	perl playtime_by_usr.pl ${date} '' ${savedir} ${filename}
fi


# save data to DB:Mysql
datadir=${svrtype}/${date}/${dev}

for playtype in ${pt[@]}
do
	python.exe update_data_into_db_date.py ${svrtype} ${dev} ${date} ${hour} ${playtype} ${datadir}/pchoke_by_hour_${playtype} ${datadir}/fbuffer_data_by_hour_${playtype}
done

# playtype '' .eq. 5
python.exe update_data_into_db_date.py ${svrtype} ${dev} ${date} ${hour} 5 ${datadir}/pchoke_by_hour_ ${datadir}/fbuffer_data_by_hour_


