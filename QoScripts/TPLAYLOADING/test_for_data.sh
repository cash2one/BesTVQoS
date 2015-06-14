#! /bin/bash
date=$1
for i in $(seq 0 11)
do
	k=$(printf "%02d" $i)
	echo "$k\n\n\n\n"
	bash stat_tplayloading_by_hour.sh $date $k 
	sleep 3
done

#bash stat_tplayloading.sh $date
