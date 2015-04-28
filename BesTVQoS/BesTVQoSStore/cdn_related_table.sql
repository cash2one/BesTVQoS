# use BesTVQoS;  source D:\p2pKernel_git\BesTVQoS\BesTVQoS\BesTVQoSStore\cdn_related_table.sql

# serverinfo table
create table IF NOT EXISTS serverinfo(
	ServerID INT NOT NULL AUTO_INCREMENT,
	IP	varchar(15) NOT NULL,
	ServiceType varchar(8),
	ISP varchar(32),
	Area varchar(64),
	PRIMARY KEY(ServerID)	
);

create unique index IP on serverinfo (IP, ServiceType, ISP, Area);

# codeinfo table
create table IF NOT EXISTS codeinfo(
	CodeID INT NOT NULL AUTO_INCREMENT,
	ServerID INT NOT NULL,
	Date date,
	Hour smallint,
	Code smallint,
	Records INT,
	Ratio float,
	PRIMARY KEY(CodeID),
	FOREIGN KEY (ServerID) REFERENCES serverinfo (ServerID)
);

create unique index ServerID on codeinfo (ServerID, Date, Hour);

# urlinfo table
create table IF NOT EXISTS urlinfo(
	URLID INT NOT NULL AUTO_INCREMENT,
	CodeID INT NOT NULL,
	URL varchar(512),
	Records INT,
	Ratio float,
	PRIMARY KEY (URLID),
	FOREIGN KEY (CodeID) REFERENCES codeinfo(CodeID)
);

# respdelayinfo table
create table IF NOT EXISTS respdelayinfo(
	URLID INT NOT NULL,
	P25 INT,
	P50 INT,
	P75 INT, 
	P90 INT, 
	P95 INT,
	AvgTime INT,
	PRIMARY KEY (URLID),
	FOREIGN KEY (URLID) REFERENCES urlinfo(URLID)
);

# reqdelayinfo table
create table IF NOT EXISTS reqdelayinfo(
	URLID INT NOT NULL,
	P25 INT,
	P50 INT,
	P75 INT, 
	P90 INT, 
	P95 INT,
	AvgTime INT,
	PRIMARY KEY (URLID),
	FOREIGN KEY (URLID) REFERENCES urlinfo(URLID)
);
