#! /bin/bash
date=$1

mkdir -p "./data/${date}"
for i in *.zip
do
	echo "unzip file: $i"
    unzip $i
    mv -f *.log "./data/${date}"
    rm $i
done

