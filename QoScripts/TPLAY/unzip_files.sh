#! /usr/bin/bash

for i in *.zip
do
	unzip $i
	rm $i
done

mv *.log log