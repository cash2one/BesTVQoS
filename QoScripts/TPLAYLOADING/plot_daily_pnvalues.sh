#! /bin/bash
date=$1

mkdir -p ./png

# 2.6.4.22
ver1="BesTV_Lite_A_2.6.4.22"
python plot_daily_pnvalues_by_stuck.py $date $ver1
python plot_daily_pnvalues_by_dbuffer.py $date $ver1

# 2.6.5.8 
ver2="BesTV_Lite_A_2.6.5.8"
python plot_daily_pnvalues_by_stuck.py $date $ver2
python plot_daily_pnvalues_by_dbuffer.py $date $ver2

python send_mail.py $date $ver1 $ver2