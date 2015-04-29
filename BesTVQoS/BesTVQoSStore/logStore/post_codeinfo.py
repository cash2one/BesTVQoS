# -*- coding: utf-8 -*- 
import json
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':    
    items=[{'IP':'192.168.16.34', 'ServiceType':'B2C', 'ISP':u'移动', 'Area':u'江苏', \
            'Date':'2015-03-24', 'Hour':23, 'Code':200, 'Records':333, 'Ratio':0.3}]
    
    json_str=json.dumps(items)
    print json_str
 #  post_tools.post_data('update/playprofile', json_str)

    url='http://127.0.0.1:81/%s'%("update/log/respcode")
    req=urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
    f=urllib2.urlopen(req)
    s=f.read()
    print s
