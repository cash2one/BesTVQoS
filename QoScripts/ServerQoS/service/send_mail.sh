#! /usr/bin/env bash

export PYTHONPATH=/usr/bin/python:/usr/bin/python2.6:/usr/lib/python2.6/site-packages

date=$(date -d yesterday +"%Y%m%d")
#date=$1

echo "|服务器IP|全天|200 OK占比|请求时长P25(s)|请求时长P50(s)|请求时长P75(s)|请求时长P90(s)|请求时长P95(s)|平均请求时长(s)|记录数|" > req_by_svrip_${date}

awk '{split(FILENAME, b, "/");if(index($0, "|24|"))printf("|%s%s\n", b[3], $0)}' B2C/${date}/*/response_data_CDF_5 | sort -t "|" -k11,11 -nr >> req_by_svrip_${date}

perl xml2html_channel_statistics.pl req_by_svrip_${date}.html req_by_svrip_${date}

echo "|服务器IP|全天|200 OK占比|响应时长P25(s)|响应时长P50(s)|响应时长P75(s)|响应时长P90(s)|响应时长P95(s)|响应请求时长(s)|记录数|" > resp_by_svrip_${date}

awk '{split(FILENAME, b, "/");if(index($0, "|24|"))printf("|%s%s\n", b[3], $0)}' B2C/${date}/*/response_data_CDF_4 | sort -t "|" -k11,11 -nr >> resp_by_svrip_${date}

perl xml2html_channel_statistics.pl resp_by_svrip_${date}.html resp_by_svrip_${date}

perl xml2html.pl code_detail_by_svrip_${date}.html code B2C/${date}/*/distribution_data_code_24

perl xml2html.pl url_detail_by_svrip_${date}.html url B2C/${date}/*/response_data_CDF_by_url_5_24

python send_mail_statistic_by_svrip.py ${date} 1.0

rm -rf req_by_svrip_${date}
rm -rf req_by_svrip_${date}.html

rm -rf resp_by_svrip_${date}
rm -rf resp_by_svrip_${date}.html

rm -rf code_detail_by_svrip_${date}.html
rm -rf url_detail_by_svrip_${date}.html
