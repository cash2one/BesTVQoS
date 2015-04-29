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

def update_url(svrtype, svrip, isp, date, area, hour, code, url, record, ratio):

   url = "http://127.0.0.1:6699/update/log/urlinfo"

   request = {}
   request['servicetype'] = svrtype
   request['svrip'] = svrip
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['code'] = code*1.0
   request['url'] = url
   request['record'] = record*1.0
   request['ratio'] = ratio*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()
        
def save_url_to_DB(filename, svrtype, svrip, isp, area, date, hour, code):
    data = np.genfromtxt(filename, delimiter="|", names="url,records,ratio", usecols=(1,2,3), dtype="S32,i8,f8")
    i = -1
    try:
        i = data['hour'].tolist().index(hour)
    except Exception, e:
        print hour, e
    
    if i == 0:
        update_code_info(svrtype, svrip, isp, date, area, hour, code, data['url'], data['records'], data['ratio'])
        print svrtype, svrip, isp, date, area, hour, code, data['url'], data['records'], data['ratio']
    
    if i > 0:
        update_code_info(svrtype, svrip, isp, date, area, hour, code, data['url'][i], data['records'][i], data['ratio'][i])
        print svrtype, svrip, isp, date, area, hour, code, data['url'][i], data['records'][i], data['ratio'][i]

def main(svrtype, svrip, date, hour, code, filename):
    isp = 'JS'
    area = 'YD'
    
    save_url_to_DB(filename, svrtype, svrip, isp, area, date, hour, code)         

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])

   
