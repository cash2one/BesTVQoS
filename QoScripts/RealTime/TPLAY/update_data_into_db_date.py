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

def update_baseinfo(time, svrtype, dev, viewtype, sucrate, fluency, records):

   url = "http://127.0.0.1:80/update/realtime/base"

   request = {}
   request['time'] = time
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['viewtype'] = viewtype
   request['sucrate'] = sucrate
   request['fluency'] = fluency
   request['records'] = '%s'%(records)
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()


def save_baseinfo_to_DB(filename1, filename2, svrtype, dev, date, hour, viewtype):
    data1 = np.genfromtxt(filename1, delimiter="|", names="hour,fluency", usecols=(1,4), dtype="S8,f8")
    data2 = np.genfromtxt(filename2, delimiter="|", names="hour,sucrate,records", usecols=(1,2,9), dtype="S8,f8,i8")
    i = -1
    k = -1
    try:
        i = data1['hour'].tolist().index(hour)
        k = data2['hour'].tolist().index(hour)
    except Exception, e:
        print hour, e
    
    
    
    if i == 0:
        update_baseinfo("%s%s"%(date,hour), svrtype, dev, viewtype, data2['sucrate'], data1['fluency'], data2['records'])
        print "%s%s"%(date,hour), svrtype, dev, viewtype, data2['sucrate'], data1['fluency'], data2['records']
        
    
    if i > 0:
        #print data1['date'][i]
        update_baseinfo("%s%s"%(date,hour), svrtype, dev, viewtype, data2['sucrate'][k], data1['fluency'][i], data2['records'][i])
        print "%s%s"%(date,hour), svrtype, dev, viewtype, data2['sucrate'][k], data1['fluency'][i], data2['records'][i]
        

def main(svrtype, dev, date, hour, viewtype, filename1, filename2):
    save_baseinfo_to_DB(filename1, filename2, svrtype, dev, date, hour, viewtype)
           
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])

