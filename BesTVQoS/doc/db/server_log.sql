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
	Records INT DEFAULT 0,
	Ratio float DEFAULT 0,
	PRIMARY KEY(CodeID),
	CONSTRAINT codeinfo_fk1 FOREIGN KEY (ServerID) REFERENCES serverinfo (ServerID) ON DELETE CASCADE
);

create unique index ServerID on codeinfo (ServerID, Date, Hour, Code);

# urlinfo table
create table IF NOT EXISTS urlinfo(
	URLID INT NOT NULL AUTO_INCREMENT,
	CodeID INT NOT NULL,
	URL varchar(512),
	Records INT DEFAULT 0,
	Ratio float DEFAULT 0,
	PRIMARY KEY (URLID),
	CONSTRAINT urlinfo_fk1 FOREIGN KEY (CodeID) REFERENCES codeinfo(CodeID) ON DELETE CASCADE
);

create unique index CodeID on urlinfo (CodeID, URL(200));

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
	CONSTRAINT respdelayinfo_fk1 FOREIGN KEY (URLID) REFERENCES urlinfo(URLID) ON DELETE CASCADE
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
	CONSTRAINT reqdelayinfo_fk1 FOREIGN KEY (URLID) REFERENCES urlinfo(URLID) ON DELETE CASCADE
);
