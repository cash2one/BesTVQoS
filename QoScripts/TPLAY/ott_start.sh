#! /usr/bin/env bash

export PYTHONPATH=/usr/bin/python:/usr/bin/python2.6:/usr/lib/python2.6/site-packages

#date=$(date +"%Y%m%d")
date=$1 

#hour=$(date -d -1hour +%H)
hour=$2 

bash prepare_for_qos.sh ${date} ${hour}

mkdir -p tmp/${date}

svr_type=('B2B' 'B2C')

for type in ${svr_type[@]}
do
	mkdir -p ${type}/${date}

	# column 6 is devType, 1 is to write subfile
	perl key_distribution_calc.pl ${type} ${date} ${hour} dev 6 1 log/${type}/TPLAY_${date}*

	bash ott_qos_by_dev.sh ${type} ${date} ${hour} ${type}/${date}/distribution_data_dev_${hour} 

	rm ${type}/${date}/distribution_data_dev_${hour}
	rm log/${type}/TPLAY_${date}*
done
