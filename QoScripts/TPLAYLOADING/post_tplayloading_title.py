# -*- coding: utf-8 -*-
import sys
import json
import urllib
import urllib2

def post_file_data(date, filename,keys):
    file=open(filename)    
    try:
        lines=file.readlines()
        for line in lines:
            line = line.rstrip('\n')
            items = line.split(" ")
            values = []
            key_value = {}
            key_value[keys[0]] = items[0]
            key_value[keys[1]] = items[1]
            if items[1] == "OTT":
                key_value[keys[1]] = "B2C"
            last_split = items[2].rfind('_')
            key_value[keys[2]] = items[2][:last_split]
            key_value[keys[3]] = items[2][last_split+1:]
            key_value[keys[4]] = items[3]

            try:
                url = 'http://127.0.0.1:6699/%s'%('tplayloading/update/title')
                values.append(key_value)
                json_str=json.dumps(values)
                print json_str
                req=urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
                f=urllib2.urlopen(req)
                s=f.read()
                print s
            except Exception, e:
                print e                
    except Exception, e:
        print e


if __name__=='__main__':
    date=sys.argv[1]
    filename=sys.argv[2]
    keys=["date", "service_type", "device_type", "version", "records"]
    post_file_data(date, filename, keys)
