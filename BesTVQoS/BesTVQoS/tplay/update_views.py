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
                try:
                    playprofile_obj.save()
                except IntegrityError, e:
                    logger.info("playprofile record already exists : %s" % (e))
                    obj=BestvPlayprofile.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        Date=create_date)
                    obj.Records=item['records']
                    obj.Users=item['users']
                    obj.AverageTime=item['avg']
                    obj.save()

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
                try:
                    playinfo_obj.save()
                except IntegrityError, e:
                    logger.info("playinfo record already exists : %s" % (e))
                    obj=BestvPlayinfo.objects.get(ServiceType=item['servicetype'],
                            DeviceType=item['dev'],
                            ISP=item['isp'],
                            Area=item['area'],
                            ViewType=item['viewtype'],
                            Date=create_date,
                            Hour=item['hour'])
                    obj.Records=item['records']
                    obj.save()     
                     
        except ValueError, e:
            result = "ValueError: %s" % e
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
                try:
                    playtime_obj.save()
                except IntegrityError, e:
                    logger.info("playtime record already exists : %s" % (e))
                    obj=BestvPlaytime.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        ViewType=item['viewtype'],
                        Date=create_date,
                        Hour=item['hour'])
                    obj.P25=item['P25']
                    obj.P50=item['P50']
                    obj.P75=item['P75']
                    obj.P90=item['P90']
                    obj.P95=item['P95']
                    obj.AverageTime=item['avg']
                    obj.save()

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
                try:
                    fbuffer_obj.save()
                except IntegrityError, e:
                    logger.info("fbuffer record already exists : %s" % (e))
                    obj=BestvFbuffer.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        ViewType=item['viewtype'],
                        Date=create_date,
                        Hour=item['hour'])
                    obj.SucRatio=item['sucratio']
                    obj.P25=item['P25']
                    obj.P50=item['P50']
                    obj.P75=item['P75']
                    obj.P90=item['P90']
                    obj.P95=item['P95']
                    obj.AverageTime=item['avg']
                    obj.save()

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
                try:
                    fluency_obj.save()
                except IntegrityError, e:
                    logger.info("fluency record already exists : %s" % (e))
                    obj=BestvFluency.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        ViewType=item['viewtype'],
                        Date=create_date,
                        Hour=item['hour'])
                    obj.Fluency=item['fluency']
                    obj.PRatio=item['pratio']
                    obj.AllPRatio=item['apratio']
                    obj.AvgCount=item['avg']
                    obj.save()

        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update fluency: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")

def bestv3Sratio(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                bestv3Sratio_obj = Bestv3SRatio(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    Date=create_date,
                    Ratio=item['ratio'])
                try:
                    bestv3Sratio_obj.save()
                except IntegrityError, e:
                    logger.info("playprofile record already exists : %s" % (e))
                    obj=Bestv3SRatio.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        Date=create_date)
                    obj.Ratio=item['ratio']
                    obj.save()

        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update bestv3Sratio: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")

def bestvavgpchoke(request):
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            for item in contents:
                create_date = '%s-%s-%s' % (
                    item['date'][0:4], item['date'][4:6], item['date'][6:8])
                bestvavgpchoke_obj = BestvAvgPchoke(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    Date=create_date,
                    AvgCount=item['avgc'],
                    AvgTime=item['avgt'])
                try:
                    bestvavgpchoke_obj.save()
                except IntegrityError, e:
                    logger.info("playprofile record already exists : %s" % (e))
                    obj=BestvAvgPchoke.objects.get(
                        ServiceType=item['servicetype'],
                        DeviceType=item['dev'],
                        ISP=item['isp'],
                        Area=item['area'],
                        Date=create_date)
                    obj.AvgCount=item['avgc']
                    obj.AvgTime=item['avgt']
                    obj.save()

        except ValueError, e:
            result = "error: %s" % e
        except Exception, e:
            result = "error: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update bestvavgpchoke: %s" % (respStr))
    return HttpResponse(respStr, content_type="application/json")