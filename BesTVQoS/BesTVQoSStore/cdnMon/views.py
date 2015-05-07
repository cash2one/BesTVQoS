# -*- coding: utf-8 -*-
import json
import logging
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

from django.http import HttpResponse
from django.db import IntegrityError

logger = logging.getLogger("django.request")

def ms_error_info(request):
    result = "ok"
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')  
        cursor = db.cursor()    
        try:               
            contents = json.loads(request.body)
            for item in contents:
                insert_sql = "INSERT INTO ms_error_info(Date, \
                        Resp, TsType, ClientIP, ClientISP, ClientArea, \
                        ServIP, ServISP, ServArea, URL, Count) \
                        VALUES ('%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s \
                        )"%(item['date'], item['resp'], item['type'], item['clientip'], item['clientisp'], item['clientarea'], \
                        item['servip'], item['servisp'], item['servarea'], item['url'], item['count'])
                try:
                    cursor.execute(insert_sql)
                    db.commit()
                except Exception, e:
                    logger.debug("error insert: %s: %s" % (insert_sql, e))
                    db.rollback() 
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update ms_error_info: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")

def ts_delay(request):
    result = "ok"
    contents=""
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')  
        cursor = db.cursor()    
        try:               
            contents = json.loads(request.body)
            for item in contents:
                insert_sql = "INSERT INTO ts_delay(Date, ServiceType, \
                        ServIP, ServArea, ServISP, Flow, InnerFlow, Info) \
                        VALUES ('%s', '%s', '%s', '%s', '%s', %s, %s, '%s')"\
                        %(item['date'], item['servicetype'], item['servip'], item['servarea'], item['servisp'], \
                        item['flow'], item['innerflow'], item['info'])
                try:
                    cursor.execute(insert_sql)
                    db.commit()
                except Exception, e:
                    logger.debug("error insert: %s: %s" % (insert_sql, e))
                    db.rollback() 
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update ms_error_info: %s, contents: %s" % (respStr, contents))
    return HttpResponse(respStr, content_type="application/json")

def province_geo(request):
    result = "ok"
    contents=""
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')  
        cursor = db.cursor()    
        try:               
            contents = json.loads(request.body)
            for item in contents:
                select_sql="select Jing, Wei from province_geo where Province='%s'"%(item['province'])
                cursor.execute(select_sql)
                record = cursor.fetchone()
                if record is not None:                    
                    if (float(item['jing'])+float(item['wei']))>0:
                        update_sql="UPDATE province_geo SET Jing=%s, Wei=%s \
                            WHERE Province='%s'"%(item['jing'], item['wei'], item['province'])
                        cursor.execute(update_sql)
                        db.commit()
                        print "update geo: %s"%update_sql
                    continue

                insert_sql = "INSERT INTO province_geo(Province, Jing, Wei) \
                        VALUES ('%s', %s, %s)"\
                        %(item['province'], item['jing'], item['wei'])
                try:
                    cursor.execute(insert_sql)
                    db.commit()
                except Exception, e:
                    logger.debug("error insert: %s: %s" % (insert_sql, e))
                    db.rollback() 
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update ms_error_info: %s, contents: %s" % (respStr, contents))
    return HttpResponse(respStr, content_type="application/json")