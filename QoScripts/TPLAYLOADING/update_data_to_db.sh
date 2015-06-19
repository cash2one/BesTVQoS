date=$1
srv_type=$2
for i in out/${srv_type}/${date}/pnvalues_${date}_*;
do
	echo $i, ${date}
	python post_tplayloading_info.py ${date} $i
done


