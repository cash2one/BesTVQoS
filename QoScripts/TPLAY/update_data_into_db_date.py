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

def update_playinfo(svrtype, dev, isp, date, area, hour, viewtype, records, users):

   url = "http://127.0.0.1:80/update/playinfo"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['viewtype'] = viewtype
   request['records'] = '%s'%(records)
   request['users'] = users
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()
   
def update_playtime(svrtype, dev, isp, date, area, hour, viewtype, p25, p50, p75, p90, p95, avg):

   url = "http://127.0.0.1:80/update/playtime"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['viewtype'] = viewtype
   request['P25'] = p25*1.0
   request['P50'] = p50*1.0
   request['P75'] = p75*1.0
   request['P90'] = p90*1.0
   request['P95'] = p95*1.0
   request['avg'] = avg*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()

def update_fbuffer(svrtype, dev, isp, date, area, hour, viewtype, sucratio, p25, p50, p75, p90, p95, avg):

   url = "http://127.0.0.1:80/update/fbuffer"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['viewtype'] = viewtype
   request['sucratio'] = sucratio*1.0
   request['P25'] = p25*1.0
   request['P50'] = p50*1.0
   request['P75'] = p75*1.0
   request['P90'] = p90*1.0
   request['P95'] = p95*1.0
   request['avg'] = avg*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()
   
def update_fluency(svrtype, dev, isp, date, area, hour, viewtype, pratio, apratio, fluency, pavg):

   url = "http://127.0.0.1:80/update/fluency"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['hour'] = hour
   request['viewtype'] = viewtype
   request['pratio'] = pratio*1.0
   request['apratio'] = apratio*1.0
   request['fluency'] = fluency*1.0
   request['avg'] = pavg*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()  

def save_playtm_to_DB(filename, svrtype, dev, isp, date, area, hour, viewtype):
    data = np.genfromtxt(filename, delimiter="|", names="hour,pratio,apratio,fluency,pavg,25,50,75,90,95,avg", usecols=(1,2,3,4,5,6,7,8,9,10,11), dtype="S8,f8,f8,f8,f8,i8,i8,i8,i8,i8,f8")
    i = -1
    try:
        i = data['hour'].tolist().index(hour)
    except Exception, e:
        print hour, e
    
    if i == 0:
        update_playtime(svrtype, dev, isp, date, area, hour, viewtype, data['25'], data['50'], data['75'], data['90'], data['95'], data['avg'])
        print svrtype, dev, isp, date, area, hour, viewtype, data['25'], data['50'], data['75'], data['90'], data['95'], data['avg']
        
        update_fluency(svrtype, dev, isp, date, area, hour, viewtype, data['pratio'], data['apratio'], data['fluency'], data['pavg'])
        print svrtype, dev, isp, date, area, hour, viewtype, data['pratio'], data['apratio'], data['fluency'], data['pavg']  

    
    if i > 0:
        #print data1['date'][i]
        update_playtime(svrtype, dev, isp, date, area, hour, viewtype, data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i])
        print svrtype, dev, isp, date, area, hour, viewtype, data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i]
        
        update_fluency(svrtype, dev, isp, date, area, hour, viewtype, data['pratio'][i], data['apratio'][i], data['fluency'][i], data['pavg'][i])
        print svrtype, dev, isp, date, area, hour, viewtype, data['pratio'][i], data['apratio'][i], data['fluency'][i], data['pavg'][i]  

       
def save_fbuffer_to_DB(filename, svrtype, dev, isp, date, area, hour, viewtype):       
    data = np.genfromtxt(filename, delimiter="|", names="hour,sucratio,25,50,75,90,95,avg,records", usecols=(1,2,3,4,5,6,7,8,9), dtype="S8,f8,i8,i8,i8,i8,i8,i8,i8")
    i = -1
    try:
        i = data['hour'].tolist().index(hour)
    except Exception, e:
        print hour, e
    
    if i == 0:
        update_fbuffer(svrtype, dev, isp, date, area, hour, viewtype, data['sucratio'], data['25'], data['50'], data['75'], data['90'], data['95'], data['avg'])
        print svrtype, dev, isp, date, area, hour, viewtype, data['sucratio'], data['25'], data['50'], data['75'], data['90'], data['95'], data['avg']
        
        update_playinfo(svrtype, dev, isp, date, area, hour, viewtype, data['records'], '0')
        print svrtype, dev, isp, date, area, hour, viewtype, data['records'], 0
    
    if i > 0:
        update_fbuffer(svrtype, dev, isp, date, area, hour, viewtype, data['sucratio'][i], data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i])
        print svrtype, dev, isp, date, area, hour, viewtype, data['sucratio'][i], data['25'][i], data['50'][i], data['75'][i], data['90'][i], data['95'][i], data['avg'][i]
        
        update_playinfo(svrtype, dev, isp, date, area, hour, viewtype, data['records'][i], '0')
        print svrtype, dev, isp, date, area, hour, viewtype, data['records'][i], 0

def main(svrtype, dev, date, hour, viewtype, filename1, filename2):
    isp = 'all'
    area = 'all'
    
    save_playtm_to_DB(filename1, svrtype, dev, isp, date, area, hour, viewtype)
    save_fbuffer_to_DB(filename2, svrtype, dev, isp, date, area, hour, viewtype)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])

