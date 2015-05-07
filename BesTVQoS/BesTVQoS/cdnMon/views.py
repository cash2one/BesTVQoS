﻿# -*- coding: utf-8 -*-

import logging
import MySQLdb
import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection
from common.views import HtmlTable
from common.date_time_tool import get_day_of_day
from common.date_time_tool import current_time

logger = logging.getLogger("django.request")

def show_ms_error(request, dev=""):
    context = {}

    date = request.GET.get("date", str(get_day_of_day(-1)))

    table = HtmlTable()
    table.mtitle = u"ms_error信息"
    table.mheader = [u"响应码", "ClientIP", u"省份", u"运营商", 'ServerIP', u'省份', u'运营商', 'url', u'次数']
    table.msub = []

    sql = "select Resp, ClientIP, ClientISP, ClientArea, ServIP, ServISP, ServArea, URL, Count \
            from ms_error_info where Date='%s'" % date

    logger.debug("Server List SQL - %s" % sql)

    cu = connection.cursor()
    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    subs = []
    for row in results:
        sub = []
        for i in range(7):
            sub.append(row[i])
        sub.append('''<a href="%s" target="_blank">%s</a>'''%(row[7], row[7]))
        sub.append(row[8])
        subs.append(sub)

    table.msub = subs

    context['table'] = table
    context['default_date'] = date

    return render_to_response('show_ms_error.html', context)

def show_tsdelay(request, dev=""):
    context = {}

    date = request.GET.get("date", str(get_day_of_day(-1)))

    table = HtmlTable()
    table.mtitle = u"CDN信息"
    table.mheader = ["ServerIP", u"省份", u"运营商", u'流量(G)', u'内网流量占比(%)', '详情']
    table.msub = []

    sql = "select ServIP, ServArea, ServISP, Flow, InnerFlow, ServiceType \
            from ts_delay where Date='%s'" % date

    logger.debug("Server List SQL - %s" % sql)

    cu = connection.cursor()
    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    subs = []
    for row in results:
        sub = []
        for i in range(3):
            sub.append(row[i])
        sub.append("%.3f"%(float(row[3])/1024/1024/1024))
        sub.append("%.1f"%(float(row[4]*1.0/row[3]*100)))
        sub.append(u'''<a href="/show_cdn_detail?ip=%s&date=%s&servicetype=%s" target="main">详情</a>'''%(row[0], date, row[5]))
        subs.append(sub)
    table.msub = subs

    context['table'] = table
    context['default_date'] = date

    return render_to_response('show_tsdelay.html', context)

# 广东+电信+4906156100+11976708_福建+电信+3268066792+10235635
def make_pie_items(ip, area, isp, info):
    pie_items=[]
    pie_item={}
    pie_item["index"] = 0
    pie_item['title']=u'流量分布（%）'
    pie_item['subtitle']='单位(G)'

    #flows
    items=info.split("_")
    flows=[]
    for i in items:
        subitems=i.split("+")
        flow_item=[]
        key='%s%s'%(subitems[0], subitems[1])
        flow_item.append(key)
        f='%.3f'%(float(subitems[2])/1024/1024/1024)
        flow_item.append(float(f))
        flows.append(flow_item)

    series = []
    serie_item = '''{
            type: 'pie',
            name: '占比',
            data: %s
        }''' % (json.dumps(flows))
    series.append(serie_item)        

    pie_item["series"] = ",".join(series)
    pie_items.append(pie_item)
    return pie_items

def make_rates(area, isp, info, tflow, percent):
    flows=[]
    items=info.split("_")
    for i in items:
        subitems=i.split("+")
        if float(subitems[2])/tflow < percent:
            break;

        flow_item={}
        flow_item["server_name"]="%s%s"%(area, isp)
        flow_item["client_name"]="%s%s"%(subitems[0], subitems[1])
        flow_item["rate"]="%d"%(float(subitems[2])/float(subitems[3]))
        flows.append(flow_item)
    return flows

def make_flows(info, tflow, percent):
    flows=[]
    items=info.split("_")
    for i in items:
        subitems=i.split("+")
        if float(subitems[2])/tflow < percent:
            break;
        flow_item={}
        flow_item["client_name"]='%s%s  %.1f'%(subitems[0], subitems[1], float(subitems[2])/tflow*100)
        flow_item["flow"]="%d"%(float(subitems[2])/float(subitems[3]))
        flows.append(flow_item)
    return flows

def get_geo_from_db(area):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    db.set_character_set('utf8')  
    cursor = db.cursor() 
    select_sql="select Jing, Wei from province_geo where Province='%s'"%(area)
    cursor.execute(select_sql)
    record = cursor.fetchone()
    if record is not None:
        return "%s,%s"%(record[0], record[1])
    return "1,1"

def get_china_geos(area, isp, info, tflow, percent):
    geos=[]
    subkey='%s%s'%(area, isp)
    item={}
    item["area"]=subkey
    item["geo"]=get_geo_from_db(area)
    geos.append(item)

    items=info.split("_")
    count=0
    for i in items:
        subitems=i.split("+")
        if float(subitems[2])/tflow < percent:
            break;

        subkey="%s%s"%(subitems[0], subitems[1])
        if subkey not in geos:
            item={}
            item["area"]=subkey
            item["geo"]=get_geo_from_db(subitems[0])
            geos.append(item)
        subkey2='%s%s  %.1f'%(subitems[0], subitems[1], float(subitems[2])/tflow*100)
        if subkey2 not in geos:
            item={}
            item["area"]=subkey2
            item["geo"]=get_geo_from_db(subitems[0])
            geos.append(item)
    return geos

def show_cdn_detail(request, dev=""):
    context = {}
    date = request.GET.get("date", str(get_day_of_day(-1)))
    servicetype=request.GET.get("servicetype", 'B2B')
    ip = request.GET.get("ip", "127.0.0.1")
    sql = "select ServArea, ServISP, Flow, InnerFlow, Info \
            from ts_delay where ServIP='%s' and ServiceType='%s' and Date='%s'" % (ip, servicetype, date)

    cu = connection.cursor()
    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    if len(results)<=0:
        return render_to_response('bestv_servers_map.html', context)

    row=results[0]
    area=row[0]
    isp=row[1]
    tflow=row[2]
    context['title']=u'服务器信息: 速率KBps'
    context['subtitle']=u'%s-%s-%s'%(area, isp, date)
    context['legendTxt']=ip

    item={}
    item["title"]=u'%s-%s-%s'%(ip, area, isp)
    info=row[4]
    context["pie_contents"]=make_pie_items(ip, area, isp, info)

    # maps
    item["geos"]=get_china_geos(area, isp, info, tflow, 0.02)
    item["rates"]=make_rates(area, isp, info, tflow, 0.02)
    item["flows"]=make_flows(info, tflow, 0.02)

    context['item']=item
    return render_to_response('bestv_servers_map.html', context)