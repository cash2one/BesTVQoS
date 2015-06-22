# -*- coding: utf-8 -*-

import json
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import IntegrityError
from common.date_time_tool import today, get_day_of_day
from common.views import set_default_values_to_cookie
from tplay.views import VIEW_TYPES, PN_LIST
from tplayloading.models import *
from tplayloading.functions import get_device_types1, get_versions1, process_tplayloading_qos

logger = logging.getLogger("django.update")

def update_info(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                version = get_version(item['service_type'], 
                        item['device_type'], item['version'])
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])

                info_obj = TPlayloadingInfo(
                    VersionId = version,
                    ISP = item['isp'],
                    Area = item['area'],
                    ChokeType = item['choketype'],
                    ViewType = item['viewtype'],
                    Date = create_date,
                    Hour = item['hour'],
                    P25 = item['P25'],
                    P50 = item['P50'],
                    P75 = item['P75'],
                    P90 = item['P90'],
                    P95 = item['P95'],
                    Records = item['records']
                    )
                try:
                    info_obj.save()
                except IntegrityError, e:
                    logger.debug("tplayloading info record already exists : %s" % (e))
                    obj = TPlayloadingInfo.objects.get(
                            VersionId = version,
                            ISP = item['isp'],
                            Area = item['area'],
                            ChokeType = item['choketype'],
                            ViewType = item['viewtype'],
                            Date = create_date,
                            Hour = item['hour'])
                    obj.P25 = item['P25']
                    obj.P50 = item['P50']
                    obj.P75 = item['P75']
                    obj.P90 = item['P90']
                    obj.P95 = item['P95']
                    obj.Records = item['records']
                    obj.save()
        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error: no post"

    resp_str = json.dumps({"result": result})
    logger.debug("update tplayloading info: %s" % (resp_str))
    return HttpResponse(resp_str, content_type="application/json")

def update_title(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                version = get_version(item['service_type'], 
                        item['device_type'], item['version'])

                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                title_obj = TPlayloadingTitle(
                    VersionId = version,
                    Date = create_date,
                    Records = item['records']
                    )
                try:
                    title_obj.save()
                except IntegrityError, e:
                    logger.debug("tplayloading title record already exists : %s" % (e))
                    obj = TPlayloadingTitle.objects.get(
                            VersionId = version,
                            Date = create_date)
                    obj.Records = item['records']
                    obj.save()
        except ValueError, e:
            result = "error1: %s" % e
        except Exception, e:
            result = "error2: %s" %e
    else:
        result = "error, no post"

    resp_str = json.dumps({"result": result})
    logger.debug("update tplayloading title: %s" %(resp_str))
    return HttpResponse(resp_str, content_type="application/json")

def get_version(service_type, device_type, version_type):
    try:
        version = VersionInfo.get_version(service_type, 
            device_type, version_type)
    except Exception, e:
        update_version(service_type, device_type, version_type)
        version = VersionInfo.get_version(service_type, device_type, version_type)

    return version

def update_version(service_type, device_type, version_type):
    result = "ok"
    try:
        version_obj = VersionInfo(
            ServiceType = service_type,
            DeviceType = device_type,
            VersionType = version_type)
        version_obj.save()
    except ValueError, e:
        result = "error: %s" % e
    except Exception, e:
        result = "error: %s" % e
    return result

STUCK = 2
DBUFFER = 3

def show_stuck(request):
    context = process_tplayloading_qos(request, TPlayloadingInfo, STUCK, 
        "卡缓冲PN值", "", "单位：秒",  VIEW_TYPES[1:], PN_LIST[0:-1])
    response = render_to_response('show_stuck.html', context)
    set_default_values_to_cookie(response, context)
    return response

def show_dbuffer(request):
    context = process_tplayloading_qos(request, TPlayloadingInfo, DBUFFER, 
        "拖动缓冲PN值", "", "单位：秒",  VIEW_TYPES[1:], PN_LIST[0:-1])
    response = render_to_response('show_dbuffer.html', context)
    set_default_values_to_cookie(response, context)
    return response

def get_device_type1(request):
    service_type = request.GET.get('service_type', "B2C")
    begin_date = request.GET.get('begin_date', str(today()))
    end_date = request.GET.get('end_date', str(today()))
    try:
        min_rec = int(request.GET.get("min_rec", '300'))
    except Exception, e:
        min_rec = 300
    
    if begin_date == str(today()) and end_date == str(today()):
        begin_date = str(get_day_of_day(-1))
        end_date = begin_date

    device_types = get_device_types1(service_type, begin_date, end_date, min_rec)
    resp_str = json.dumps({"device_types": device_types})

    return HttpResponse(resp_str, content_type="text/json")

def get_version1(request):
    service_type = request.GET.get('service_type', "B2C")
    device_type = request.GET.get('device_type', "")
    begin_date = request.GET.get('begin_date', str(today()))
    end_date = request.GET.get('end_date', str(today()))
    min_rec = request.GET.get("min_rec", '300')
    try:
        min_rec = int(request.GET.get("min_rec", '300'))
    except Exception, e:
        min_rec = 300
        
    if begin_date == str(today()) and end_date == str(today()):
        begin_date = str(get_day_of_day(-1))
        end_date = begin_date

    versions = get_versions1(service_type, device_type, begin_date, end_date, min_rec)
    resp_str = json.dumps({"versions": versions})

    return HttpResponse(resp_str, content_type="text/json")

