#! /bin/bash
date=$1
hour=$2
b2b_type=$3
outdir=$4

mkdir -p "./data/${b2b_type}/${date}"
for i in *.zip
do
	echo "unzip file: $i"
    unzip $i
    cat *.log > TPLAYLOADING_${date}${hour}_${b2b_type}.log
    mv -f TPLAYLOADING_${date}${hour}_${b2b_type}.log ${outdir}
    rm $i
    rm -rf *.log
done

