#! /usr/bin/bash

date=$(date +"%Y%m%d")
#date=$1 

# $(date +"%H")
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

	if [ ${hour} -ne 24 ]; then
		rm ${type}/${date}/distribution_data_dev_${hour}
	fi

	rm log/${type}/TPLAY_${date}*
done
