# -*- coding: utf-8 -*-
import json
import logging
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from django.http import HttpResponse
# from django.db import IntegrityError

logger = logging.getLogger("django.request")


def execute_insert(db, cursor, insert_sql, update_sql=""):
    try:
        cursor.execute(insert_sql)
        db.commit()
    except Exception, e:
        logger.debug("error insert: %s: %s" % (insert_sql, e))
        db.rollback()
        if len(update_sql) > 0:
            cursor.execute(update_sql)
            db.commit()


def get_ServerID(db, cursor, IP, ServiceType, ISP, Area, Type=''):
    serverID = 0
    query_sql = "select ServerID from serverinfo where IP='%s' and ServiceType='%s' \
                    and ISP='%s' and Area='%s'" % (IP, ServiceType, ISP, Area)
    print query_sql
    cursor.execute(query_sql)
    record = cursor.fetchone()
    if record is None:
        insert_sql = "INSERT INTO serverinfo(IP,\
            ServiceType, ISP, Area, Type)\
            VALUES ('%s', '%s', '%s', '%s', '%s')" % (IP, ServiceType, ISP, Area, Type)
        execute_insert(db, cursor, insert_sql)
        #serverID = cursor.lastrowid
        cursor.execute(query_sql)
        record = cursor.fetchone()
        serverID = record[0]
    else:
        serverID = record[0]

    return serverID


def get_CodeID(db, cursor,  IP, ServiceType, ISP, Area, Date, Hour, Code, Type=''):
    codeID = 0
    serverID = get_ServerID(db, cursor,  IP, ServiceType, ISP, Area, Type)
    query_sql = "select CodeID from codeinfo where ServerID=%d and Date='%s' \
                    and Hour=%s and Code=%d" % (serverID, Date, Hour, Code)
    print query_sql
    cursor.execute(query_sql)
    record = cursor.fetchone()
    if record is None:
        insert_sql = "INSERT INTO codeinfo(ServerID, Date, Hour, Code)\
            VALUES (%d, '%s', %s, %d)" % (serverID, Date, Hour, Code)
        execute_insert(db, cursor, insert_sql)
        #codeID = cursor.lastrowid
        cursor.execute(query_sql)
        record = cursor.fetchone()
        codeID = record[0]
    else:
        codeID = record[0]

    return codeID


def get_URLID(db, cursor,  IP, ServiceType, ISP, Area, Date, Hour, Code, URL, Type=''):
    urlID = 0
    codeID = get_CodeID(db, cursor,  IP, ServiceType, ISP, Area, Date, Hour, Code, Type)
    query_sql = "select URLID from urlinfo where CodeID=%d and URL='%s'" % (codeID, URL)
    print query_sql
    cursor.execute(query_sql)
    record = cursor.fetchone()
    if record is None:
        insert_sql = "INSERT INTO urlinfo(CodeID, URL) VALUES (%d, '%s')" % (codeID, URL)
        execute_insert(db, cursor, insert_sql)
        #urlID = cursor.lastrowid
        cursor.execute(query_sql)
        record = cursor.fetchone()
        urlID = record[0]
    else:
        urlID = record[0]

    return urlID


def respcode(request):
    result = "ok"
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')
        cursor = db.cursor()
        try:
            contents = json.loads(request.body)
            for item in contents:
                serverID = get_ServerID(db, cursor, item['ip'], item['servicetype'], item['isp'], item['area'], item['type'])
                insert_codeinfo_sql = "INSERT INTO codeinfo(ServerID, Date, Hour, Code, Records, Ratio)\
                        VALUES (%d, '%s', %s, %d, %d, %f)" \
                        % (serverID, item['date'], item['hour'], item['code'], item['records'], item['ratio'])
                update_codeinfo_sql = "UPDATE codeinfo SET Records=%d, Ratio=%f \
                        WHERE ServerID=%d and Date='%s' and Hour=%s and Code=%d"\
                        % (item['records'], item['ratio'], serverID, item['date'], item['hour'], item['code'])
                execute_insert(db, cursor, insert_codeinfo_sql, update_codeinfo_sql)
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update respcode: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def urlinfo(request):
    result = "ok"
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')
        cursor = db.cursor()
        try:
            contents = json.loads(request.body)
            for item in contents:
                codeID = get_CodeID(db, cursor, item['ip'], item['servicetype'], item['isp'], item['area'],
                                    item['date'], item['hour'], item['code'], item['type'])
                insert_urlinfo_sql = "INSERT INTO urlinfo(CodeID, URL, Records, Ratio)\
                        VALUES (%d, '%s', %d, %f)" % (codeID, item['url'], item['records'], item['ratio'])
                update_urlinfo_sql = "UPDATE urlinfo SET Records=%d, Ratio=%f \
                          WHERE CodeID=%d and URL='%s'" \
                          % (item['records'], item['ratio'], codeID, item['url'])
                execute_insert(db, cursor, insert_urlinfo_sql, update_urlinfo_sql)
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update urlinfo: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def handle_delay(request, table):
    result = "ok"
    if request.method == "POST":
        db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
        db.set_character_set('utf8')
        cursor = db.cursor()
        try:
            contents = json.loads(request.body)
            for item in contents:
                urlID = get_URLID(db, cursor, item['ip'], item['servicetype'], item['isp'], item['area'],
                                  item['date'], item['hour'], item['code'], item['url'], item['type'])
                insert_delay_sql = "INSERT INTO %s(URLID, P25, P50, P75, P90, P95, AvgTime)\
                        VALUES (%d, %d, %d, %d, %d, %d, %d)"\
                        % (table, urlID, item['P25'], item['P50'], item['P75'],
                           item['P90'], item['P95'], item['avg'])
                update_delay_sql = "UPDATE %s SET P25=%d, P50=%d, P75=%d, P90=%d, P95=%d, AvgTime=%d \
                        WHERE URLID=%d" % (table, item['P25'], item['P50'], item['P75'],
                                           item['P90'], item['P95'], item['avg'], urlID)
                execute_insert(db, cursor, insert_delay_sql, update_delay_sql)
        except ValueError, e:
            result = "valueerror: %s" % e
        except Exception, e:
            result = "error: %s|%s" % (e, contents)

        db.close()
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update %s: %s" % (table, respStr))
    return HttpResponse(respStr, content_type="application/json")


def respdelay(request):
    return handle_delay(request, "respdelayinfo")


def reqdelay(request):
    return handle_delay(request, "reqdelayinfo")
