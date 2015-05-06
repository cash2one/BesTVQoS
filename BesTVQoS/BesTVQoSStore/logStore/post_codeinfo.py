# -*- coding: utf-8 -*-
import json
# import urllib
import urllib2

if __name__ == '__main__':
    items = [{'ip': '192.168.16.34', 'servicetype': 'B2C', 'isp': u'移动', 'area': u'江苏', 'type': 'AAA',
              'date': '2015-03-24', 'hour': 23, 'code': 200, 'records': 333, 'ratio': 0.3}]

    json_str = json.dumps(items)
    print json_str
    print "hello"
 #  post_tools.post_data('update/playprofile', json_str)

    url = 'http://127.0.0.1:81/%s' % ("update/log/respcode")
    req = urllib2.Request(url, json_str, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    s = f.read()
    print s
