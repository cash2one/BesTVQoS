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
done

# for '' - unknown
perl fbuffer_cdf_by_hour.pl ${date} ${hour} '' ${savedir} ${filename}
perl pchoke_ratio_by_hour.pl ${date} ${hour} '' ${savedir} ${filename}

# save data to DB:Mysql
datadir=${svrtype}/${date}/${dev}

for playtype in ${pt[@]}
do
	python update_data_into_db_date.py ${svrtype} ${dev} ${date} ${hour} ${playtype} ${datadir}/pchoke_by_hour_${playtype} ${datadir}/fbuffer_data_by_hour_${playtype}
done

# playtype '' .eq. 5
python update_data_into_db_date.py ${svrtype} ${dev} ${date} ${hour} 5 ${datadir}/pchoke_by_hour_ ${datadir}/fbuffer_data_by_hour_


# for all day
if [ ${hour} -eq 24 ]; then
	perl playtime_by_usr.pl ${date} ${savedir} ${filename}
	python update_playprofile_into_db_date.py ${svrtype} ${dev} ${date} ${datadir}/playtm_by_usr
	
	# for BesTV
	perl BesTV_fbuffer_cdf_by_day.pl ${date} ${savedir} ${filename}
	perl BesTV_pchoke_ratio_by_day.pl ${date} ${savedir} ${filename}
	
	python BesTV_update_data_into_db_date.py ${svrtype} ${dev} ${date} ${datadir}/BesTV_fbuffer_3s_ratio_data ${datadir}/BesTV_avg_pchoke_data
fi

