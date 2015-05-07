# use BesTVQoS;  source D:\xxx.sql

# serverinfo table
drop table if exists province_geo;
create table IF NOT EXISTS province_geo(
	Province varchar(64) NOT NULL,
	Jing FLOAT,
	Wei Float,
	PRIMARY KEY(Province)	
);