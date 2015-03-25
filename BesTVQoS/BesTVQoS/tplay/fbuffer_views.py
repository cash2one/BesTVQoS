﻿# -*- coding: utf-8 -*- 
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db.models import Count, Min, Sum, Avg
from tplay.models import *
from common.mobile import do_mobile_support
from common.views import *
from common.date_time_tool import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]

#1-点播，2-回看，3-直播，4-连看, 5-unknown
VIEW_TYPES=[(0, u"总体"), (1, u"点播"), (2, u"回看"), (3, u"直播"), (4, u"连看"), (5, u"未知")]
#VIEW_TYPES_DES={0: u"总体", 1:u"点播", 2:u"回看", 3:u"直播", 4:u"连看", 5:u"unknown"}

hour_xalis=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
            "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]

PNVALUES_LIST=["P25", "P50", "P75", "P90", "P95", "AVG"]
PNVALUES_LIST_DES={"P25":"P25", "P50":"P50", "P75":"P75", "P90":"P90", "P95":"P95", "AVG":"AVG"}

class NoDataError(Exception):
    def __init__(self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

'''
 For single Qos, such as sucration, fluency, pchoeratio, display: plot of all view types
 Filter parameters: ServiceType, DeviceType, Begin_date, End_date

'''

def get_filter_param_values(request, table_name):
    service_type=request.GET.get("service_type", "All")
    device_type=request.GET.get("device_type")
    last_date=str(today())
    begin_date=request.GET.get("begin_date", last_date)
    end_date=request.GET.get("end_date", last_date)

    logger.info("get_filter_values: %s - %s"%(service_type, device_type))

    device_types = get_device_types(table_name, service_type, begin_date, end_date)
    if device_type is None or device_type=="": # init device type first time
        device_type = device_types[0]    

    return service_type, device_type, device_types, begin_date, end_date

def get_filter_objs_by_device_types(device_type, begin_date, end_date, table):
    device_filter_ojbs = table.objects.filter(DeviceType=device_type,
                                           Date__gte=begin_date, Date__lte=end_date)
    return device_filter_ojbs

def get_Qos_value_of_table(obj, table_name, Qos_name):
    if table_name=="fbuffer":
        if Qos_name=="SucRatio":
            return obj.SucRatio
        else:
            return 0
    elif table_name=="fluency":
        if Qos_name=="Fluency":
            return obj.Fluency
        elif Qos_name=="PRatio":
            return obj.PRatio
        elif Qos_name=="AllPRatio":
            return obj.AllPRatio
        elif Qos_name=="AvgCount":
            return obj.AvgCount
        return 0
    else:
        return 0


# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, xAlis, title, subtitle, ytitle):
    item={}
    item["index"]=item_idx
    item["title"]=title #u"首次缓冲成功率"
    item["subtitle"]=subtitle #u"全天24小时/全类型"
    item["y_title"]=ytitle #u"成功率"
    item["xAxis"]=xAlis
    item["t_interval"]=1

    series=[]
    for (i, desc) in keys:
        serie_item='''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }'''%(desc, ",".join(key_values[i]))
        series.append(serie_item)
    item["series"]=",".join(series)
    return item

def prepare_hour_data_of_single_Qos(objs, view_types, Qos_name):
    data_by_hour={}
    display_if_has_data=False
    for i in view_types:
        view_idx=i[0]
        data_by_hour[view_idx]=[]
        if view_idx == 0:
            filter_objs=objs;
        else:
            filter_objs=objs.filter(ViewType=view_idx)
        for hour in range(24):
            try:
                obj=filter_objs.filter(Hour=hour).aggregate(sum=Sum(Qos_name))
                tmp=obj["sum"]
                if tmp is None:
                    tmp = 0
                data_by_hour[view_idx].append("%s"%(tmp))
                #obj=filter_objs.get(Hour=hour)
                #sucratio_by_hour[i].append("%s"%(get_Qos_value_of_table(obj, table_name, Qos_name)))
                display_if_has_data=True
            except Exception, e:
                data_by_hour[view_idx].append("0")

    if display_if_has_data==False:
        return None
    return data_by_hour

def prepare_daily_data_of_single_Qos(objs, days_region, view_types, Qos_name):
    data_by_day={}
    display_if_has_data=False
    for i in view_types:
        view_idx=i[0]
        data_by_day[view_idx]=[]
        if view_idx==0:
            filter_objs=objs
        else:
            filter_objs=objs.filter(ViewType=view_idx)

        for date_idx in days_region:
            try:
                obj=filter_objs.filter(Date=date_idx, Hour=24).aggregate(sum=Sum(Qos_name))
                tmp=obj["sum"]
                if tmp is None:
                    tmp = 0
                data_by_day[view_idx].append("%s"%(tmp))
                display_if_has_data=True
            except Exception, e:
                data_by_day[view_idx].append("%s"%(0))

    if display_if_has_data==False:
        return None
    return data_by_day

# service_type, device_type, begin_date, end_date
def process_single_Qos(request, table, Qos_name, title, subtitle, ytitle, view_types):
    begin_time=current_time()
    items=[]

    try:
        # get fileter params
        service_type, device_type, device_types, begin_date, end_date = get_filter_param_values(request, table)
        if device_type=="":
            raise NoDataError("No data between %s - %s in %s"%(begin_date, end_date, table_name))

        device_filter_ojbs = get_filter_objs_by_device_types(device_type, begin_date, end_date, table)

        # process data from databases;
        if begin_date==end_date:
            data_by_hour=prepare_hour_data_of_single_Qos(device_filter_ojbs, view_types, Qos_name)      
            if data_by_hour is None:
                raise NoDataError("No hour data between %s - %s"%(begin_date, end_date))
            item=make_plot_item(data_by_hour, view_types, 0, hour_xalis, title, subtitle, ytitle)
            items.append(item)
        else:
            days_region=get_days_region(begin_date, end_date)
            data_by_day=prepare_daily_data_of_single_Qos(device_filter_ojbs, days_region, view_types, Qos_name)
            if data_by_day is None:
                raise NoDataError("No daily data between %s - %s"%(begin_date, end_date))
            item=make_plot_item(data_by_day, view_types, 0, days_region, title, subtitle, ytitle)
            items.append(item)

    except Exception, e:
        logger.info("query %s %s error: %s"%("xxx", Qos_name, e))

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

    logger.info("query fbuffer sucratio, cost: %s"%(current_time()-begin_time))

    return context

def show_fbuffer_sucratio(request, dev=""):
    context = process_single_Qos(request, BestvFbuffer, "SucRatio", u"首次缓冲成功率", u"全类型", u"成功率", VIEW_TYPES[1:])
    do_mobile_support(request, dev, context)
    return render_to_response('show_fbuffer_sucratio.html', context)

def show_fluency(request, dev=""):
    context = process_single_Qos(request, BestvFluency, "Fluency", u"一次不卡比例", u"全类型", u"百分比", VIEW_TYPES[1:])
    do_mobile_support(request, dev, context)
    return render_to_response('show_fluency.html', context)

def show_fluency_pratio(request, dev=""):
    context = process_single_Qos(request, BestvFluency, "PRatio", u"卡用户卡时间比", u"全类型", u"百分比", VIEW_TYPES[1:])
    do_mobile_support(request, dev, context)
    return render_to_response('show_fluency_pratio.html', context)

def show_fluency_allpratio(request, dev=""):
    context = process_single_Qos(request, BestvFluency, "AllPRatio", u"所有用户卡时间比", u"全类型", u"百分比", VIEW_TYPES[1:])
    do_mobile_support(request, dev, context)
    return render_to_response('show_fluency_allpratio.html', context)

def show_fluency_avgcount(request, dev=""):
    context = process_single_Qos(request, BestvFluency, "AvgCount", u"卡用户平均卡次数", u"全类型", u"百分比", VIEW_TYPES[1:])
    do_mobile_support(request, dev, context)
    return render_to_response('show_fluency_avgcount.html', context)



'''
 For multi Qos, such as pnvalue, display: multi plots of single viewtype
 Filter parameters: ServiceType, DeviceType, Begin_date, End_date

'''


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
    begin_time=current_time()
    items=[]

    try:
        # init params
        service_type, device_type, device_types, begin_date, end_date = get_filter_param_values(request, "fbuffer")
        if device_type=="":
            raise NoDataError("No data between %s - %s"%(begin_date, end_date))

        device_filter_ojbs = BestvFbuffer.objects.filter(DeviceType=device_type,
                                           Date__gte=begin_date, Date__lte=end_date)

        # process data from databases;
        if begin_date==end_date:
            data_by_hour=prepare_fbuffer_pnvalue_hour_data(device_filter_ojbs) 
            if data_by_hour is None:
                raise NoDataError("No hour data between %s - %s"%(begin_date, end_date))
                  
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
            if data_by_day is None:
                raise NoDataError("No daily data between %s - %s"%(begin_date, end_date))

            item_idx=0
            for view_type_idx in VIEW_TYPES:
                item=make_plot_item(data_by_day[view_type_idx], PNVALUES_LIST, PNVALUES_LIST_DES,
                                    item_idx, days_region, 
                                    u"缓冲成PN值", u"全天24小时%s"%(VIEW_TYPES_DES[view_type_idx]), u"秒")
                items.append(item)
                item_idx+=1
            
    except Exception, e:
        logger.info("query fbuffer time error: %s"%(e))

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

    do_mobile_support(request, dev, context)

    logger.info("query fbuffer time, cost: %s"%(current_time()-begin_time))

    return render_to_response('show_fbuffer_time.html', context)