# 在serverinfo表中增加服务类型字段（AAA、EPG...）
alter table serverinfo add Type varchar(64);

# 更新现有服务器记录
update serverinfo set Type='AAA' 
where IP='10.50.131.4' or IP='10.50.131.5' or IP='10.50.131.104' or IP='10.50.131.105' or IP='10.49.1.38' or IP='10.49.1.39';

update serverinfo set Type='EPG' 
where IP='10.50.131.106' or IP='10.50.131.6' or IP='10.50.131.7' or IP='10.50.131.112' or IP='10.50.131.113' or IP='10.50.131.114'
or IP='10.49.1.7' or IP='10.49.1.8' or IP='10.49.1.9' or IP='10.49.1.10';

update serverinfo set Type='PS' 
where IP='10.50.131.8' or IP='10.50.131.9' or IP='10.50.131.17' or IP='10.50.131.18' or IP='10.49.1.40' or IP='10.49.1.41';

update serverinfo set Type='BSD' 
where IP='10.50.131.110' or IP='10.50.131.111' or IP='10.50.131.10';