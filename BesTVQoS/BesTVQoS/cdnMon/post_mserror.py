# -*- coding: utf-8 -*- 
import json
import urllib
import urllib2

if __name__ == '__main__':    
    items=[{'date':'2015-03-24', 'resp':200, 'clientip':'192.168.16.34', 'clientisp':u'移动2', 'clientarea':u'江苏', \
            'servtip':'192.168.16.34', 'servisp':u'移动', 'servarea':u'江苏', 'url':'http://mytest.com'}]
    
    json_str=json.dumps(items)
    print json_str
    print "hello"
 #  post_tools.post_data('update/playprofile', json_str)

    url='http://127.0.0.1:81/%s'%("update/mon/mserror")
    req=urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
    f=urllib2.urlopen(req)
    s=f.read()
    print s
