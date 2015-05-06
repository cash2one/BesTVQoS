# use BesTVQoS;  source D:\p2pKernel_git\BesTVQoS\BesTVQoS\BesTVQoSStore\cdn_related_table.sql

#/*==============================================================*/
#/* View: view_codeinfo                                          */
#/*==============================================================*/
drop view if exists view_codeinfo;
create view view_codeinfo  as
select IP, ServiceType, ISP, Area, Type, Date, Hour, Code, Records, Ratio 
from serverinfo, codeinfo 
where serverinfo.ServerID = codeinfo.ServerID;


#/*==============================================================*/
#/* View: view_urlinfo                                           */
#/*==============================================================*/
drop view if exists view_urlinfo;
create view view_urlinfo  as
select IP, ServiceType, ISP, Area, Type, Date, Hour, Code, URL, urlinfo.Records, urlinfo.Ratio 
from serverinfo, codeinfo, urlinfo 
where serverinfo.ServerID = codeinfo.ServerID and codeinfo.CodeID = urlinfo.CodeID;


#/*==============================================================*/
#/* View: view_respdelayinfo                                     */
#/*==============================================================*/
drop view if exists view_respdelayinfo;
create view view_respdelayinfo  as
select  IP, ServiceType, ISP, Area, Type, Date, Hour, Code, URL, P25, P50, P75, P90, P95, AvgTime, urlinfo.Records
from serverinfo, codeinfo, urlinfo, respdelayinfo
where serverinfo.ServerID = codeinfo.ServerID and codeinfo.CodeID = urlinfo.CodeID and urlinfo.URLID = respdelayinfo.URLID;


#/*==============================================================*/
#/* View: view_reqdelayinfo                                      */
#/*==============================================================*/
drop view if exists view_reqdelayinfo;
create view view_reqdelayinfo  as
select IP, ServiceType, ISP, Area, Type, Date, Hour, Code, URL, P25, P50, P75, P90, P95, AvgTime, urlinfo.Records
from serverinfo, codeinfo, urlinfo, reqdelayinfo
where serverinfo.ServerID = codeinfo.ServerID and codeinfo.CodeID = urlinfo.CodeID and urlinfo.URLID = reqdelayinfo.URLID;


#/*==============================================================*/
#/* View: view_sum_records                                       */
#/*==============================================================*/
drop view if exists view_sum_records;
create view view_sum_records as 
select Date, ServerID, sum(Records) as Records 
from codeinfo 
where Hour<24 group by Date, ServerID;


#/*==============================================================*/
#/* View: view_sum_ok_records                                    */
#/*==============================================================*/
drop view if exists view_sum_ok_records;
create view view_sum_ok_records as 
select Date, ServerID, sum(Records) as Records 
from codeinfo 
where Code=200 and Hour<24 group by Date, ServerID;


#/*==============================================================*/
#/* View: view_sum_ok_ratio                                      */
#/*==============================================================*/
drop view if exists view_sum_ok_ratio;
create view view_sum_ok_ratio as 
select m.Date, m.ServerID, (m.Records/n.Records) as Ratio, n.Records as Records 
from view_sum_ok_records as m, view_sum_records as n 
where m.ServerID=n.ServerID and m.Date=n.Date;


#/*==============================================================*/
#/* View: view_servers_status                                    */
#/*==============================================================*/
drop view if exists view_servers_status;
create view view_servers_status as 
select Date, ServiceType, Area, ISP, Type, IP, t.Ratio, t.Records 
from serverinfo as s, view_sum_ok_ratio as t 
where s.ServerID=t.ServerID order by Ratio;