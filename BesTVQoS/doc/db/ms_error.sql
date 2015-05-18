# use BesTVQoS;  source D:\xxx.sql

# serverinfo table
drop table if exists ms_error_info;
create table IF NOT EXISTS ms_error_info(
	RecordID INT NOT NULL AUTO_INCREMENT,
	Date date,
	Resp smallint,
	TsType smallint,
	ClientIP	varchar(15) NOT NULL,
	ClientISP varchar(32),
	ClientArea varchar(64),
	ServIP	varchar(15) NOT NULL,
	ServISP varchar(32),
	ServArea varchar(64),
	URL varchar(512),
	Count smallint,
	ContentLen INT,
	PRIMARY KEY(RecordID)	
);

create unique index ClientIP on ms_error_info (ClientIP, ServIP, Date, URL(200));