# -*- coding: utf-8 -*- 
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response
from tplay.models import *
from common.views import *
from common.date_time_tool import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]

#1-点播，2-回看，3-直播，4-连看, 5-unknown
VIEW_TYPES=[1, 2, 3, 4, 5]
VIEW_TYPES_DES={1:u"点播", 2:u"回看", 3:u"直播", 4:u"连看", 5:u"unknown"}

hour_xalis=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
            "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]

PNVALUES_LIST=["P25", "P50", "P75", "P90", "P95", "AVG"]
PNVALUES_LIST_DES={"P25":"P25", "P50":"P50", "P75":"P75", "P90":"P90", "P95":"P95", "AVG":"AVG"}

class NoDataError(Exception):
    def __init__(self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

def get_filter_values(request, table_name):
    service_type=request.GET.get("service_type", "All")
    device_type=request.GET.get("device_type")
    last_date=str(today())
    begin_date=request.GET.get("begin_date", last_date)
    end_date=request.GET.get("end_date", last_date)

    logger.info("get_filter_values: %s - %s"%(service_type, device_type))

    device_types = get_device_types(table_name, service_type, begin_date, end_date)
    if device_type is None or device_type=="": # init device type first time
        if len(device_types)>0:
            device_type = device_types[0]
        else:
            device_types.append("")
            device_type = ""

    return service_type, device_type, device_types, begin_date, end_date

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, keys_description, item_idx, xAlis, title, subtitle, ytitle):
    item={}
    item["index"]=item_idx
    item["title"]=title #u"首次缓冲成功率"
    item["subtitle"]=subtitle #u"全天24小时/全类型"
    item["y_title"]=ytitle #u"成功率"
    item["xAxis"]=xAlis
    item["t_interval"]=1

    series=[]
    for i in keys:
        serie_item='''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }'''%(keys_description[i], ",".join(key_values[i]))
        series.append(serie_item)
    item["series"]=",".join(series)
    return item

def prepare_fbuffer_sucratio_hour_data(fbuffer_objs):
    sucratio_by_hour={}
    for i in VIEW_TYPES:
        sucratio_by_hour[i]=[]
        filter_objs=fbuffer_objs.filter(ViewType=i)
        for hour in range(24):
            try:
                obj=filter_objs.get(Hour=hour)
                sucratio_by_hour[i].append("%s"%(obj.SucRatio))
            except Exception, e:
                sucratio_by_hour[i].append("0")
    return sucratio_by_hour

def prepare_fbuffer_sucratio_daily_data(fbuffer_objs, days_duration):
    sucratio_by_day={}
    for i in VIEW_TYPES:
        sucratio_by_day[i]=[]
        filter_objs=fbuffer_objs.filter(ViewType=i)
        for date_idx in days_duration:
            try:
                obj=filter_objs.get(Date=date_idx, Hour=24)
                sucratio_by_day[i].append("%s"%(obj.SucRatio))
            except Exception, e:
                sucratio_by_day[i].append("%s"%(0))
    return sucratio_by_day


def show_fbuffer_sucratio(request, dev=""):
    items=[]

    try:
        # get fileter params
        service_type, device_type, device_types, begin_date, end_date = get_filter_values(request, "fbuffer")
        if device_type=="":
            raise NoDataError("No data between %s - %s"%(begin_date, end_date))

        device_filter_ojbs = BestvFbuffer.objects.filter(DeviceType=device_type,
                                           Date__gte=begin_date, Date__lte=end_date)

        # process data from databases;
        if begin_date==end_date:
            data_by_hour=prepare_fbuffer_sucratio_hour_data(device_filter_ojbs)         
            item=make_plot_item(data_by_hour, VIEW_TYPES, VIEW_TYPES_DES, 0, hour_xalis, u"首次缓冲成功率", u"全天24小时/全类型", u"成功率")
            items.append(item)
        else:
            days_region=get_days_region(begin_date, end_date)
            data_by_day=prepare_fbuffer_sucratio_daily_data(device_filter_ojbs, days_region)
            item=make_plot_item(data_by_day, VIEW_TYPES, VIEW_TYPES_DES, 0, days_region, u"首次缓冲成功率", u"全类型", u"成功率")
            items.append(item)

    except Exception, e:
        logger.info("query fbuffer sucratio error: %s"%(e))

    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents']=items
    if len(items)>0:
        context['has_data']=True

    return render_to_response('show_fbuffer_sucratio.html', context)

# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}
def prepare_fbuffer_pnvalue_hour_data(fbuffer_objs):
    sucratio_by_hour={}
    for i in VIEW_TYPES:
        filter_objs=fbuffer_objs.filter(ViewType=i)
        display_data={}
        for pn_idx in PNVALUES_LIST:
            display_data[pn_idx]=[]

        display_if_has_data=False
        for hour in range(24):
            try:
                obj=filter_objs.get(Hour=hour)
                display_data[PNVALUES_LIST[0]].append("%s"%(obj.P25))
                display_data[PNVALUES_LIST[1]].append("%s"%(obj.P50))
                display_data[PNVALUES_LIST[2]].append("%s"%(obj.P75))
                display_data[PNVALUES_LIST[3]].append("%s"%(obj.P90))
                display_data[PNVALUES_LIST[4]].append("%s"%(obj.P95))
                display_data[PNVALUES_LIST[5]].append("%s"%(obj.AverageTime))
                display_if_has_data=True
            except Exception, e:
                display_data[PNVALUES_LIST[0]].append("%s"%(0))
                display_data[PNVALUES_LIST[1]].append("%s"%(0))
                display_data[PNVALUES_LIST[2]].append("%s"%(0))
                display_data[PNVALUES_LIST[3]].append("%s"%(0))
                display_data[PNVALUES_LIST[4]].append("%s"%(0))
                display_data[PNVALUES_LIST[5]].append("%s"%(0))

        if display_if_has_data:
            sucratio_by_hour[i]=display_data

    if len(sucratio_by_hour)==0:
        return None
    return sucratio_by_hour

# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}
def prepare_fbuffer_pnvalue_daily_data(fbuffer_objs, days_duration):
    sucratio_by_day={}
    for i in VIEW_TYPES:                
        filter_objs=fbuffer_objs.filter(ViewType=i)
        display_data={}
        for pn_idx in PNVALUES_LIST:
            display_data[pn_idx]=[]

        display_if_has_data=False
        for date_idx in days_duration:
            try:
                obj=filter_objs.get(Date=date_idx, Hour=24)
                display_data[PNVALUES_LIST[0]].append("%s"%(obj.P25))
                display_data[PNVALUES_LIST[1]].append("%s"%(obj.P50))
                display_data[PNVALUES_LIST[2]].append("%s"%(obj.P75))
                display_data[PNVALUES_LIST[3]].append("%s"%(obj.P90))
                display_data[PNVALUES_LIST[4]].append("%s"%(obj.P95))
                display_data[PNVALUES_LIST[5]].append("%s"%(obj.AverageTime))
                display_if_has_data=True
            except Exception, e:
                display_data[PNVALUES_LIST[0]].append("%s"%(0))
                display_data[PNVALUES_LIST[1]].append("%s"%(0))
                display_data[PNVALUES_LIST[2]].append("%s"%(0))
                display_data[PNVALUES_LIST[3]].append("%s"%(0))
                display_data[PNVALUES_LIST[4]].append("%s"%(0))
                display_data[PNVALUES_LIST[5]].append("%s"%(0))

        if display_if_has_data:
            sucratio_by_day[i]=display_data

    if len(sucratio_by_day)==0:
        return None
    return sucratio_by_day

# key-values: key: P25, values:[...]
def make_fbuffer_pnvalue_item(key_values, item_idx, xAlis, title, subtitle, ytitle):
    item={}
    item["index"]=item_idx
    item["title"]=title #u"缓冲时长"
    item["subtitle"]=subtitle #u"点播"
    item["y_title"]=ytitle #u"成功率"
    item["xAxis"]=xAlis
    item["t_interval"]=1

    series=[]
    for i in PNVALUES_LIST:
        serie_item='''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }'''%(i, ",".join(key_values[i]))
        series.append(serie_item)
    item["series"]=",".join(series)
    return item


def show_fbuffer_time(request, dev=""):
    items=[]

    try:
        # init params
        service_type, device_type, device_types, begin_date, end_date = get_filter_values(request, "fbuffer")
        if device_type=="":
            raise NoDataError("No data between %s - %s"%(begin_date, end_date))

        device_filter_ojbs = BestvFbuffer.objects.filter(DeviceType=device_type,
                                           Date__gte=begin_date, Date__lte=end_date)

        # process data from databases;
        if begin_date==end_date:
            data_by_hour=prepare_fbuffer_pnvalue_hour_data(device_filter_ojbs)       
            item_idx=0
            for view_type_idx in VIEW_TYPES:
                item=make_plot_item(data_by_hour[view_type_idx], PNVALUES_LIST, PNVALUES_LIST_DES,
                                    item_idx, hour_xalis, 
                                    u"缓冲成PN值", u"全天24小时%s"%(VIEW_TYPES_DES[view_type_idx]), u"秒")
                items.append(item)
                item_idx+=1
        else:
            days_region=get_days_region(begin_date, end_date)
            data_by_day=prepare_fbuffer_pnvalue_daily_data(device_filter_ojbs, days_region)
            item_idx=0
            for view_type_idx in VIEW_TYPES:
                item=make_plot_item(data_by_day[view_type_idx], PNVALUES_LIST, PNVALUES_LIST_DES,
                                    item_idx, days_region, 
                                    u"缓冲成PN值", u"全天24小时%s"%(VIEW_TYPES_DES[view_type_idx]), u"秒")
                items.append(item)
                item_idx+=1
            
    except Exception, e:
        logger.info("query fbuffer sucratio error: %s"%(e))

    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents']=items
    if len(items)>0:
        context['has_data']=True

    return render_to_response('show_fbuffer_time.html', context)
