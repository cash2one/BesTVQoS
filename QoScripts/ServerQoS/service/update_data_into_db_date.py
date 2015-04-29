#! /usr/bin/env python2.7

import urllib2
import json

import random

import numpy as np
#import pylab as pl
from datetime import *
import sys
#from __main__ import name
#from pylab import *

reload(sys)
sys.setdefaultencoding("utf-8")

def update_code_info(svrtype, svrip, isp, area, date, hour, code, records, ratio):

   url = "http://127.0.0.1:6699/update/log/respcode"

   request = {}
   request['servicetype'] = svrtype
   request['ip'] = svrip
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['code'] = code
   request['records'] = '%s'%(records)
   request['ratio'] = '%.2f'%(ratio)
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()


def update_time(datatype, svrtype, svrip, isp, area, date, hour, url, p25, p50, p75, p90, p95, avg):

   url = "http://127.0.0.1:6699/update/log/%s"%(datatype)
   
   request = {}
   request['servicetype'] = svrtype
   request['ip'] = svrip
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['url'] = url
   request['P25'] = p25*1000
   request['P50'] = p50*1000
   request['P75'] = p75*1000
   request['P90'] = p90*1000
   request['P95'] = p95*1000
   request['avg'] = avg*1000
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()

def save_tm_to_DB(filename, datatype, svrtype, svrip, isp, area, date, hour, url):
    data = np.genfromtxt(filename, delimiter="|", names="hour,25,50,75,90,95,avg", usecols=(1,3,4,5,6,7,8,9), dtype="f8,f8,f8,f8,f8,f8")
    i = -1
    try:
        i = data['hour'].tolist().index(hour)
    except Exception, e:
        print hour, e
    
    if i == 0:
        update_time(datatype, svrtype, svrip, isp, area, date, hour, url, data['25'], data['50'], data['75'], data['90'], data['95'], data['avg'])
        print datatype, svrtype, svrip, isp, area, date, hour, url, data['25'], data['50'], data['75'], data['90'], data['95'], data['avg']
    
    if i > 0:
        #print data1['date'][i]
        update_time(datatype, svrtype, svrip, isp, date, area, hour, url, data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i])
        print datatype, svrtype, svrip, isp, date, area, hour, url, data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i]
       
def save_code_to_DB(filename, svrtype, svrip, isp, area, date, hour):       
    data = np.genfromtxt(filename, delimiter="|", names="code,records,ratio", usecols=(1,2,3), dtype="i8,i8,f8")
        
    i = len(data['code'])
    if i == 1:
        update_code_info(svrtype, svrip, isp, date, area, hour, data['code'], data['records'], data['ratio'])
        print svrtype, svrip, isp, date, area, hour, data['code'], data['records'], data['ratio']
        return
    
    for k in range(i):
        update_code_info(svrtype, svrip, isp, date, area, hour, data['code'][k], data['records'][k], data['ratio'][k])
        print svrtype, svrip, isp, date, area, hour, data['code'][k], data['records'][k], data['ratio'][k]
    

def main(svrtype, svrip, date, hour, filename1, filename2, filename3):
    isp = 'OTT'
    area = 'OTT'
    
    save_tm_to_DB(filename1, 'reqdelay', svrtype, svrip, isp, area, date, hour, 'all')
    save_tm_to_DB(filename2, 'respdelay', svrtype, svrip, isp, area, date, hour, 'all')
    save_code_to_DB(filename3, svrtype, svrip, isp, area, date, hour)
           
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])

   
