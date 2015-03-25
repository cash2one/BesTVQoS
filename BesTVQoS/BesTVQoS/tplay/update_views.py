# -*- coding: utf-8 -*-

import json
import logging

from django.http import HttpResponse
from django.db import IntegrityError
from tplay.models import *

logger = logging.getLogger("django.request")


def playprofile(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                playprofile_obj = BestvPlayprofile(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    Date=create_date,
                    Records=item['records'],
                    Users=item['users'],
                    AverageTime=item['avg'])
                playprofile_obj.save()
        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update playprofile: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def playinfo(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                playinfo_obj = BestvPlayinfo(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'],
                    Records=item['records'])
                playinfo_obj.save()
        except ValueError, e:
            result = "ValueError: %s" % e
        except IntegrityError, e:
            result = "update record: %s" % e
            obj=BestvPlayinfo.objects.get(ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'])
            obj.Records=item['records']
            obj.save()            
        except Exception, e:
            result = "Exception: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update playinfo: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def playtime(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                playtime_obj = BestvPlaytime(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'],
                    P25=item['P25'],
                    P50=item['P50'],
                    P75=item['P75'],
                    P90=item['P90'],
                    P95=item['P95'],
                    AverageTime=item['avg'])
                playtime_obj.save()
        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update playtime: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def fbuffer(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                fbuffer_obj = BestvFbuffer(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'],
                    SucRatio=item['sucratio'],
                    P25=item['P25'],
                    P50=item['P50'],
                    P75=item['P75'],
                    P90=item['P90'],
                    P95=item['P95'],
                    AverageTime=item['avg'])
                fbuffer_obj.save()
        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update fbuffer: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")


def fluency(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                fluency_obj = BestvFluency(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'],
                    Fluency=item['fluency'],
                    PRatio=item['pratio'],
                    AllPRatio=item['apratio'],
                    AvgCount=item['avg'])
                fluency_obj.save()
        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update fluency: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")
