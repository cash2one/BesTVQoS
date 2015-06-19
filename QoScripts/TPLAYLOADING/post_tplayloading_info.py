# -*- coding: utf-8 -*-
import sys
import json
import urllib
import urllib2

def post_file_data(date, filename,keys):
    file=open(filename)    
    try:
        lines=file.readlines()
        values=[]
        for line in lines:
            line = line.rstrip('\n')
            items = line.split(" ")
            key_value={}
            for i in range(len(keys)):
                key_value[keys[i]] = items[i]    

            # append version, isp, area
            key_value['isp'] = 'all'
            key_value['area'] = 'all'
            if key_value['service_type'] == "OTT":
                key_value['service_type'] = "B2C"
            temp = key_value['device_type']
            last_split = temp.rfind('_')
            key_value['device_type'] = temp[:last_split]
            key_value['version'] = temp[last_split+1:]
            values.append(key_value)
            
            if len(values) == 8:
                post_values(values)
                values = []

        if values:
            print "hello"
            post_values(values)
                          
    except Exception, e:
        print e

def post_values(values):
    try:
        url = 'http://127.0.0.1:6699/%s'%('tplayloading/update/info')
        print len(values)
        json_str=json.dumps(values)
        print json_str
        req=urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
        f=urllib2.urlopen(req)
        s=f.read()
        print s
    except Exception, e:
        print e  

if __name__=='__main__':
    date = sys.argv[1]
    filename = sys.argv[2]
    keys=["date", "hour", "service_type", "device_type", "viewtype", "choketype", "P25", "P50", "P75", "P90", "P95", 'records']
    post_file_data(date, filename, keys)
