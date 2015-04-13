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

def update_playprofile(svrtype, dev, isp, date, area, avg, users, records):

   url = "http://10.100.12.5:6699/update/playprofile"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['records'] = records*1.0
   request['users'] = users*1.0
   request['avg'] = avg*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()
       
def save_playprofile_to_DB(filename, svrtype, dev, isp, date, area):       
    data = np.genfromtxt(filename, delimiter="|", names="avg,users,records", usecols=(7,8,9), dtype="f8,i8,i8")
        
    update_playprofile(svrtype, dev, isp, date, area, data['avg'], data['users'], data['records'])
    print svrtype, dev, isp, date, area, data['avg'], data['users'], data['records']

def main(svrtype, dev, date, filename):
    isp = 'all'
    area = 'all'
    
    save_playprofile_to_DB(filename, svrtype, dev, isp, date, area)
           

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])



   
