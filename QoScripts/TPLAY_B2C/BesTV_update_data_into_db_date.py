#! /usr/bin/env python2.7

import urllib2
import json

import numpy as np
from datetime import *
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

def update_fbuffer_3s_ratio_data(svrtype, dev, isp, date, area, ratio):

   url = "http://10.100.12.5:80/update/bestv3Sratio"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['ratio'] = ratio*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()

def update_avg_pchoke_data(svrtype, dev, isp, date, area, avgc, avgt):

   url = "http://10.100.12.5:80/update/bestvavgpchoke"

   request = {}
   request['servicetype'] = svrtype
   request['dev'] = dev
   request['isp'] = isp
   request['area'] = area
   request['date'] = date
   request['avgc'] = avgc*1.0
   request['avgt'] = avgt*1.0
   
   items = []
   items.append(request)
   
   req = urllib2.Request(url, headers={'Content-Type': 'application/json; charset=utf-8'},
                         data = json.dumps(items))

   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

   response = opener.open(req)

   print response.read()
       
def save_fbuffer_3s_ratio_to_DB(filename, svrtype, dev, isp, date, area):       
    data = np.genfromtxt(filename, delimiter="|", names="ratio", usecols=(2), dtype="f8")
        
    update_fbuffer_3s_ratio_data(svrtype, dev, isp, date, area, data['ratio'])
    print svrtype, dev, isp, date, area, data['ratio']


def save_avg_pchoke_data_to_DB(filename, svrtype, dev, isp, date, area):       
    data = np.genfromtxt(filename, delimiter="|", names="avgc,avgt", usecols=(2,3), dtype="f8,f8")
        
    update_avg_pchoke_data(svrtype, dev, isp, date, area, data['avgc'], data['avgt'])
    print svrtype, dev, isp, date, area, data['avgc'], data['avgt']


def main(svrtype, dev, date, filename1, filename2):
    isp = 'all'
    area = 'all'
    
    save_fbuffer_3s_ratio_to_DB(filename1, svrtype, dev, isp, date, area)
    save_avg_pchoke_data_to_DB(filename2, svrtype, dev, isp, date, area)      

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])



   