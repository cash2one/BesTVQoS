# -*- coding: utf-8 -*-

"""
Definition of views.
"""

import logging
import json
import platform
if platform.system() != "Windows":
    import redis

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context
from django.db import connection
from django.contrib.auth.decorators import login_required
from common.navi import Navi
from common.date_time_tool import today, current_time, todaystr

logger = logging.getLogger("django.request")


class HtmlTable:
    mtitle = "title"
    mheader = ["header"]
    msub = [['sub1'], ['sub2']]
   

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, xAlis, title, subtitle, ytitle):
    item = {}
    item["index"] = item_idx
    item["title"] = title  # u"首次缓冲成功率"
    item["subtitle"] = subtitle  # u"全天24小时/全类型"
    item["y_title"] = ytitle  # u"成功率"
    item["xAxis"] = xAlis
    item["t_interval"] = 1
    if len(xAlis) > 30:
        item["t_interval"] = len(xAlis) / 30

    series = []
    for (i, desc) in keys:
        serie_item = '''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }''' % (desc, ",".join(key_values[i]))
        series.append(serie_item)
    item["series"] = ",".join(series)
    return item


def get_cell_width(num_characters):
    return int((1+num_characters) * 256)

# 
def write_xls(book, sheet, rowx, headings, data, heading_xf, data_xf):
    for colx, value in enumerate(headings):
        try:
            width = get_cell_width(len(value))
        except Exception, e:
            width = -1
        if width > sheet.col(colx).width:
            sheet.col(colx).width = width
        sheet.write(rowx, colx, value, heading_xf)

    for row in data:
        rowx+=1
        for colx, value in enumerate(row):
            try:
                width = get_cell_width(len(value))
            except Exception, e:
                width = -1
            if width > sheet.col(colx).width:
                sheet.col(colx).width = width
            sheet.write(rowx, colx, value, data_xf)

    return rowx


def write_remarks_to_xls(book, sheet, rowx, data, data_xf):
    for value in data:
        sheet.write(rowx, 0, value, data_xf)
        rowx+=1

    return rowx

@login_required
def home(request):
    logger.debug("Qos request")
    return render_to_response('index.html', Context())

@login_required
def p_home(request):
    return render_to_response('home.html', Context())

@login_required
def m_home(reuest):
    context = {}
    context["is_mobile"] = True
    context["top_title"] = "BesTV QoS Monitor"
    #context["navi"] = Navi().get_sub_items()

    return render_to_response('m_navi_menu.html', context)

@login_required
def navi(request, target_url=""):
    if target_url:
        navi = Navi()
        navi_path = navi.get_path(request.path)
        context = {}
        context["navi"] = navi.get_sub_items(request.path)
        context["is_mobile"] = True
        context["top_title"] = navi_path[-1].name
        context["show_topbar"] = True
        context["path"] = navi_path[:-1]
        return render_to_response('m_navi_menu.html', context)
    else:
        return m_home(request)

def get_types_from_cache(table, begin_date, end_date, type_name, base_name):
    if platform.system() == "Windows":
        return None
    types_key = "%s:%s:%s:%s:%s" % (type_name, base_name, table, begin_date, end_date)
    try:
        redis_cache = redis.StrictRedis(host='localhost', port=6379, db=2)
        types_list = redis_cache.lrange(types_key, 0, -1)
        logger.info("get redis cache suc: %s" % len(types_list))
        return types_list
    except:
        logger.info("get redis cache fail: %s" % (types_key))
        return None

def cache_types(table, begin_date, end_date, type_name, base_name, types_list):
    if platform.system() == "Windows":
        return None
    types_key = "%s:%s:%s:%s:%s" % (type_name, base_name, table, begin_date, end_date)
    try:
        redis_cache = redis.StrictRedis(host='localhost', port=6379, db=2)
        for item in types_list:
            redis_cache.rpush(types_key, item)
        base_date = todaystr()
        if cmp(begin_date, base_date) < 0 and cmp(end_date, base_date) < 0:
            redis_cache.expire(types_key, 3600*2)
        else:
            redis_cache.expire(types_key, 1500)
        logger.info("cache device types suc: %s" % len(types_list))
    except Exception, e:
        logger.info("cache deivce types fail: %s" % e)

DEVICE_KEY = "devices"
DEVICE_KEY_BASE = "all"
VERSION_KEY = "versions"

def get_device_types1(table, service_type, begin_date, end_date, cu=None):
    # get devices type from cache
    devices_list = get_types_from_cache(table, begin_date, end_date, DEVICE_KEY, DEVICE_KEY_BASE)
    if devices_list:
        return devices_list

    fitlers = "where Date >= '%s' and Date <= '%s'" % (begin_date, end_date)
    if service_type != "All":
        fitlers = fitlers + " and ServiceType = '%s'" % (service_type)
    sql_command = "select distinct DeviceType from %s %s" % (table, fitlers)
    sql_command += " and DeviceType not like '%.%'"

    if cu is None:
        cu = connection.cursor()

    logger.debug("SQL %s" % sql_command)
    cu.execute(sql_command)

    device_types = []
    for item in cu.fetchall():
        device_types.append(item[0].encode('utf-8'))

    if len(device_types) == 0:
        device_types = ['']

    # cache devices type
    cache_types(table, begin_date, end_date, DEVICE_KEY, DEVICE_KEY_BASE, device_types)

    return device_types

def get_table_name(url):
    table_name = ""
    if url.find("playing_trend") != -1:
        table_name = "playinfo"
    elif url.find("fbuffer") != -1:
        table_name = "fbuffer"
    elif url.find("play_time") != -1:
        table_name = "playtime"
    elif url.find("fluency") != -1:
        table_name = "fluency"
    elif url.find("3sratio") != -1:
        table_name = "bestv3sratio"
    elif url.find("avg_pcount") != -1 or url.find("avg_ptime") != -1:
        table_name = "bestvavgpchoke"
    elif url.find("reporter") != -1:
        table_name = "playinfo"

    return table_name

@login_required
def get_device_type(request, dev=""):
    respStr = json.dumps({"device_types": []})
    if(request.method == 'GET'):
        try:
            service_type = request.GET.get('service_type')
            begin_date = request.GET.get('begin_date')
            end_date = request.GET.get('end_date')
            url = request.META.get('HTTP_REFERER')

            table_name = get_table_name(url)

            device_types = get_device_types1(
                table_name, service_type, begin_date, end_date)
            respStr = json.dumps({"device_types": device_types})

        except Exception, e:
            raise e

    return HttpResponse(respStr, content_type="text/json")


def get_versions1(table, service_type, device_type, begin_date, end_date, cu=None):
    # get devices type from cache
    versions_list = get_types_from_cache(table, begin_date, end_date, 
        VERSION_KEY, device_type)
    if versions_list:
        return versions_list

    fitlers = "where Date >= '%s' and Date <= '%s'" % (begin_date, end_date)
    if service_type != "All":
        fitlers = fitlers + " and ServiceType = '%s'" % (service_type)
    fitlers += " and DeviceType like '%s_%%'" % (device_type)
    sql_command = "select distinct DeviceType from %s %s" % (table, fitlers)

    if cu is None:
        cu = connection.cursor()

    logger.debug("SQL %s" % sql_command)
    cu.execute(sql_command)

    version_pos = len(device_type) + 1
    version_types = []
    for item in cu.fetchall():
        version_types.append(item[0][version_pos:])

    # cache devices type
    cache_types(table, begin_date, end_date, VERSION_KEY, device_type, 
        version_types)

    return version_types

@login_required
def get_version(request, dev=""):
    respStr = json.dumps({"versions": []})
    if(request.method == 'GET'):
        try:
            service_type = request.GET.get('service_type')
            device_type = request.GET.get('device_type')
            begin_date = request.GET.get('begin_date')
            end_date = request.GET.get('end_date')
            url = request.META.get('HTTP_REFERER')

            table_name = get_table_name(url)

            versions = get_versions1(
                table_name, service_type, device_type, begin_date, end_date)
            respStr = json.dumps({"versions": versions})

        except Exception, e:
            raise e

    return HttpResponse(respStr, content_type="text/json")


def get_default_values_from_cookie(request):
    filter_map = json.loads('{"st":"B2C","dt":"","vt":"","begin":"%s","end":"%s"}' % (
        today(), today()))
    try:
        filter_map = json.loads(request.COOKIES["bestvFilters"])
        if("st" not in filter_map or "dt" not in filter_map or "vt" not in filter_map or
                "begin" not in filter_map or "end" not in filter_map):
            raise Exception()
    except:
        logger.info("Loads Cookie['bestvFilters'] failed! ")

    return filter_map


def set_default_values_to_cookie(response, context):
    response.set_cookie("bestvFilters",
                        json.dumps({"st": context["default_service_type"],
                                    "dt": context["default_device_type"],
                                    "vt": context["default_version"],
                                    "begin": context['default_begin_date'],
                                    "end": context['default_end_date']}),
                        max_age=30000)

def get_filter_param_values(request, table):
    begin_time = current_time()
    filters_map = get_default_values_from_cookie(request)
    service_type = request.GET.get("service_type", filters_map["st"]).encode("utf-8")
    device_type = request.GET.get("device_type", filters_map["dt"]).encode("utf-8")
    version = request.GET.get("version", filters_map["vt"]).encode("utf-8")
    begin_date = request.GET.get("begin_date", filters_map["begin"]).encode("utf-8")
    end_date = request.GET.get("end_date", filters_map["end"]).encode("utf-8")
    logger.info("get_filter_values: %s - %s - %s" %
                (service_type, device_type, version))

    device_types = get_device_types1(table, service_type, begin_date, end_date)
    if len(device_types) == 0:
        device_types = [""]
        device_type = ""

    if device_type not in device_types:
        device_type = device_types[0]
    logger.info("get_filter_param_values1 %s %s, cost: %s" %
                (device_type, version, (current_time() - begin_time)))

    versions = []
    try:        
        versions = get_versions1(
            table, service_type, device_type, begin_date, end_date)
    except Exception, e:
        logger.info("get_versions(%s, %s, %s, %s, %s) failed." % (
            table, service_type, device_type, begin_date, end_date))

    if len(versions) == 0:
        versions = [""]
        version = ""
    if version not in versions:
        version = versions[0]

    logger.info("get_filter_param_values %s %s, cost: %s" %
                (device_type, version, (current_time() - begin_time)))
    return service_type, device_type, device_types, version, versions, begin_date, end_date

def get_report_filter_param_values(request, table):
    service_type, device_type, device_types, version, versions, begin_date, end_date = get_filter_param_values(request, table)
    version2 = request.GET.get("version2", "").encode("utf-8")
    versions2 = versions
    return service_type, device_type, device_types, version, versions, version2, versions2, begin_date, end_date
