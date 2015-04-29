# -*- coding: utf-8 -*- 
import json
import urllib
import urllib2

if __name__ == '__main__':    
    items=[{'IP':'192.168.16.38', 'ServiceType':'B2C', 'ISP':u'移动', 'Area':u'江苏', \
            'Date':'2015-03-24', 'Hour':23, 'Code':200, 'URL':'all', \
            'P25':1, 'P50':2, 'P75':3, 'P90':4, 'P95':5, 'AVG':3}]
    
    json_str=json.dumps(items)
    print json_str
 #  post_tools.post_data('update/playprofile', json_str)

    url='http://127.0.0.1:81/%s'%("update/log/reqdelay")
    req=urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
    f=urllib2.urlopen(req)
    s=f.read()
    print s
