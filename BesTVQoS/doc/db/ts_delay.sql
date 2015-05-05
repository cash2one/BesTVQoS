# use BesTVQoS;  source D:\xxx.sql

# serverinfo table
drop table if exists ts_delay;
create table IF NOT EXISTS ts_delay(
	RecordID INT NOT NULL AUTO_INCREMENT,
	Date date,
	ServiceType varchar(8),
	ServIP	varchar(15) NOT NULL,
	ServArea varchar(64),
	ServISP varchar(32),	
	Flow Bigint,
	Info varchar(900),
	PRIMARY KEY(RecordID)	
);

create unique index ServIP on ts_delay (ServIP, ServiceType, Date);