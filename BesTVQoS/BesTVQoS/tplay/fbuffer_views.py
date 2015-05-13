# -*- coding: utf-8 -*-
import logging
import MySQLdb

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from common.mobile import do_mobile_support
from common.views import get_filter_param_values, set_default_values_to_cookie
from common.date_time_tool import current_time, get_days_offset, \
    today, get_days_region

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["B2B", "B2C"]

VIEW_TYPES = [
    (0, "总体"), (1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")]

HOUR_XAXIS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
              "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]

PNVALUES_LIST = [("P25", "P25"), ("P50", "P50"), ("P75", "P75"),
                 ("P90", "P90"), ("P95", "P95"), ("AVG", "AVG")]
PNVALUES_LIST_DES = {"P25": "P25", "P50": "P50",
                     "P75": "P75", "P90": "P90", "P95": "P95", "AVG": "AVG"}


class NoDataError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

'''
 For single Qos, such as sucration, fluency, pchoeratio, display: plot of all view types
 Filter parameters: ServiceType, DeviceType, Begin_date, End_date

'''

class FilterParams:
    def __init__(self, table, servicetype, devicetype, begin_date, end_date):
        self.table = table
        self.servicetype = servicetype
        self.devicetype = devicetype
        self.begin_date = begin_date
        self.end_date = end_date

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, xaxis, title, subtitle, ytitle):
    item = {}
    item["index"] = item_idx
    item["title"] = title  # "首次缓冲成功率"
    item["subtitle"] = subtitle  # "全天24小时/全类型"
    item["y_title"] = ytitle  # "成功率"
    item["xAxis"] = xaxis
    item["t_interval"] = 1
    if len(xaxis) > 30:
        item["t_interval"] = len(xaxis) / 30

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


def prepare_hour_data_of_single_Qos(filter_params, view_types, qos_name, base_radix):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()

    data_by_hour = {}
    display_if_has_data = False
    for i in view_types:
        begin_time = current_time()
        view_idx = i[0]
        data_by_hour[view_idx] = []
        sql = "SELECT %s, Hour FROM %s WHERE DeviceType='%s' and Date >= '%s' \
            and Date <= '%s' and Hour<24" % (qos_name, filter_params.table, \
            filter_params.devicetype, filter_params.begin_date, \
            filter_params.end_date)
        if filter_params.servicetype != 'All':
            sql = "%s and ServiceType='%s'" % (sql, filter_params.servicetype)
        if view_idx > 0:
            sql = "%s and ViewType=%d" % (sql, view_idx)

        tmp_list = [0.0 for k in range(24)]
        cursor.execute(sql)
        results = cursor.fetchall()
        logger.info("execute sql:  %s, cost: %s" %
                (sql, (current_time() - begin_time)))
        for row in results:
            tmp_list[row[1]] += row[0]
            if row[0] > 0:
                display_if_has_data = True
                    
        data_by_hour[view_idx] = ['%s' % (k * base_radix) for k in tmp_list]

    mysql_db.close()
    if display_if_has_data == False:
        return None
    return data_by_hour


def prepare_daily_data_of_single_Qos(filter_params, days_region, view_types, qos_name, hour_flag, base_radix):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()
   
    data_by_day = {}
    display_if_has_data = False
    for i in view_types:
        begin_time = current_time()
        view_idx = i[0]
        data_by_day[view_idx] = []
        sql = "SELECT %s, Date FROM %s WHERE DeviceType='%s' and \
            Date >= '%s' and Date <= '%s'" % (qos_name, filter_params.table, \
            filter_params.devicetype, filter_params.begin_date, 
            filter_params.end_date)
        if filter_params.servicetype != 'All':
            sql = "%s and ServiceType='%s'" % (sql, filter_params.servicetype)
        if hour_flag:
            sql = "%s and Hour=24" % sql
        if view_idx != 0:
            sql = "%s and ViewType=%d" % (sql, view_idx)

        tmp_list = [0.0 for k in days_region]
        cursor.execute(sql)
        results = cursor.fetchall()
        logger.info("execute sql:  %s, cost: %s" %
                (sql, (current_time() - begin_time)))
        for row in results:
            tmp_idx = get_days_offset(days_region[0], str(row[1]))
            tmp_list[tmp_idx] += row[0]
            if row[0]>0:
                display_if_has_data = True

        data_by_day[view_idx] = ['%s' % (k * base_radix) for k in tmp_list]

    mysql_db.close()
    if display_if_has_data == False:
        return None
    return data_by_day

# hour_flag: if have hour data, True


def process_single_Qos(request, table, qos_name, title, subtitle, ytitle, view_types, hour_flag, base_radix=1):
    begin_time = current_time()
    items = []
    service_type = "All"
    device_type = ""
    device_types = [""]
    version = ""
    versions = [""]
    begin_date = today()
    end_date = today()

    try:
        (service_type, device_type, device_types, 
            version, versions, begin_date, end_date) = get_filter_param_values(request, table)
        
        if device_type == "":
            raise NoDataError("No data between %s - %s in %s" % (begin_date, end_date, table))

        if version == "All":
            device_type_full = device_type
        else:
            device_type_full = '%s_%s' % (device_type, version) 

        filterParams=FilterParams(table, service_type, device_type_full, begin_date, end_date)

        # process data from databases;
        if begin_date == end_date and hour_flag == True:
            data_by_hour = prepare_hour_data_of_single_Qos(
                filterParams, view_types, qos_name, base_radix)
            if data_by_hour is None:
                raise NoDataError(
                    "No hour data between %s - %s" % (begin_date, end_date))
            item = make_plot_item(data_by_hour, view_types, 
                0, HOUR_XAXIS, title, subtitle, ytitle)
            items.append(item)
        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_daily_data_of_single_Qos(
                filterParams, days_region, view_types, qos_name, hour_flag, base_radix)
            if data_by_day is None:
                raise NoDataError(
                    "No daily data between %s - %s" % (begin_date, end_date))

            format_days_region = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
            item = make_plot_item(data_by_day, view_types, 0, 
                format_days_region, title, subtitle, ytitle)
            items.append(item)

    except Exception, e:
        logger.info("query %s %s error: %s" % (str(table), qos_name, e))

    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents'] = items
    if len(items) > 0:
        context['has_data'] = True

    logger.info("query %s %s, cost: %s" %
                (str(table), qos_name, (current_time() - begin_time)))

    return context


@login_required
def show_fbuffer_sucratio(request, dev=""):
    context = process_single_Qos(
        request, "fbuffer", "SucRatio", "首次缓冲成功率", "加载成功的播放次数/播放总次数", \
        "成功率(%)", VIEW_TYPES[1:], True, 100)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_fbuffer_sucratio.html', context)
    set_default_values_to_cookie(response, context)

    return response
    # return render_to_response('show_fbuffer_sucratio.html', context)


@login_required
def show_fluency(request, dev=""):
    context = process_single_Qos(
        request, "fluency", "Fluency", "一次不卡比例", "无卡顿播放次数/加载成功的播放次数", \
        "百分比(%)", VIEW_TYPES[1:], True, 100)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_fluency.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_pratio(request, dev=""):
    context = process_single_Qos(
        request, "fluency", "PRatio", "卡用户卡时间比", "卡顿总时长/卡顿用户播放总时长", \
        "百分比(%)", VIEW_TYPES[1:], True, 100)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_fluency_pratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_allpratio(request, dev=""):
    context = process_single_Qos(
        request, "fluency", "AllPRatio", "所有用户卡时间比", "卡顿总时长/所有用户播放总时长", \
        "百分比(%)", VIEW_TYPES[1:], True, 100)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_fluency_allpratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_avgcount(request, dev=""):
    context = process_single_Qos(
        request, "fluency", "AvgCount", "卡顿播放平均卡次数", "卡顿总次数/卡顿播放数", \
        "次数", VIEW_TYPES[1:], True)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_fluency_avgcount.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_3sratio(request, dev=""):
    context = process_single_Qos(
        request, "bestv3sratio", "Ratio", "3秒起播占比", "首次载入时长小于等于3秒的播放次数/播放总次数", \
        "百分比(%）", VIEW_TYPES[0:1], False, 100)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_3sratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_avg_pcount(request, dev=""):
    context = process_single_Qos(
        request, "bestvavgpchoke", "AvgCount", "每小时播放卡顿平均次数", \
        "卡顿次数/卡顿用户播放总时长（小时）", "次数", VIEW_TYPES[0:1], False)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_avg_pcount.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_avg_ptime(request, dev=""):
    context = process_single_Qos(
        request, "bestvavgpchoke", "AvgTime", "每小时播放卡顿平均时长", \
        "卡顿总时长（秒）/卡顿用户播放总时长（小时）", "秒", VIEW_TYPES[0:1], False)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_avg_ptime.html', context)
    set_default_values_to_cookie(response, context)

    return response


# For multi Qos, such as pnvalue, display: multi plots of single viewtype
#Filter parameters: ServiceType, DeviceType, Begin_date, End_date

# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}
def prepare_pnvalue_hour_data(filter_params, view_types, pnvalue_types, base_radix):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()

    data_by_hour = {}
    for (i, _) in view_types:
        sql = "SELECT Hour, P25, P50, P75, P90, P95, AverageTime \
            FROM %s WHERE DeviceType='%s' and Date >= '%s' and \
            Date <= '%s' and Hour<24 and ViewType=%d" % (
            filter_params.table, filter_params.devicetype, 
            filter_params.begin_date, filter_params.end_date, i)
        if filter_params.servicetype != 'All':
            sql = "%s and ServiceType='%s'" % (sql, filter_params.servicetype)
        display_data = {}
        for (pn_idx, _) in pnvalue_types:
            display_data[pn_idx] = ["0" for k in range(24)]

        display_if_has_data = False
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            display_data[pnvalue_types[0][0]][row[0]] = "%s" % (row[1] / base_radix)
            display_data[pnvalue_types[1][0]][row[0]] = "%s" % (row[2] / base_radix)
            display_data[pnvalue_types[2][0]][row[0]] = "%s" % (row[3] / base_radix)
            display_data[pnvalue_types[3][0]][row[0]] = "%s" % (row[4] / base_radix)
            display_data[pnvalue_types[4][0]][row[0]] = "%s" % (row[5] / base_radix)
            display_data[pnvalue_types[5][0]][row[0]] = "%s" % (row[6] / base_radix)
            if row[1]+row[2]+row[3]+row[4]+row[5]+row[6]>0:
                display_if_has_data = True

        if display_if_has_data:
            data_by_hour[i] = display_data

    mysql_db.close()
    if len(data_by_hour) == 0:
        return None
    return data_by_hour

# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}


def prepare_pnvalue_daily_data(filterParams, days_region, view_types, pnvalue_types, base_radix):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = db.cursor()

    data_by_day = {}
    for (i, _) in view_types:
        sql = "SELECT Date, P25, P50, P75, P90, P95, AverageTime \
            FROM %s WHERE DeviceType='%s' and Date >= '%s' and \
            Date <= '%s' and Hour=24 and ViewType=%d" % (
            filterParams.table, filterParams.devicetype, 
            filterParams.begin_date, filterParams.end_date, i)
        if filter_params.servicetype != 'All':
            sql = "%s and ServiceType='%s'" % (sql, filter_params.servicetype)
        display_data = {}
        for (pn_idx, _) in pnvalue_types:
            display_data[pn_idx] = ["0" for k in days_region]

        display_if_has_data = False
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            tmp_idx = get_days_offset(days_region[0], str(row[0]))
            display_data[pnvalue_types[0][0]][tmp_idx] = "%s" % (row[1] / base_radix)
            display_data[pnvalue_types[1][0]][tmp_idx] = "%s" % (row[2] / base_radix)
            display_data[pnvalue_types[2][0]][tmp_idx] = "%s" % (row[3] / base_radix)
            display_data[pnvalue_types[3][0]][tmp_idx] = "%s" % (row[4] / base_radix)
            display_data[pnvalue_types[4][0]][tmp_idx] = "%s" % (row[5] / base_radix)
            display_data[pnvalue_types[5][0]][tmp_idx] = "%s" % (row[6] / base_radix)
            if row[1]+row[2]+row[3]+row[4]+row[5]+row[6]>0:
                display_if_has_data = True

        if display_if_has_data:
            data_by_day[i] = display_data
    
    db.close()
    if len(data_by_day) == 0:
        return None
    return data_by_day


def process_multi_plot(request, table, title, subtitle, ytitle, view_types, pnvalue_types, base_radix=1):
    begin_time = current_time()
    items = []
    service_type = "All"
    device_type = ""
    device_types = [""]
    version = ""
    versions = [""]
    begin_date = today()
    end_date = today()

    try:
        # init params
        (service_type, device_type, device_types, 
            version, versions, begin_date, end_date) = get_filter_param_values(request, table)
        if device_type == "":
            raise NoDataError("No data between %s - %s" %
                              (begin_date, end_date))

        if version == "All":
            device_type_full = device_type
        else:
            device_type_full = '%s_%s' % (device_type, version) 

        filter_params=FilterParams(table, service_type, device_type_full, begin_date, end_date)

        # process data from databases;
        if begin_date == end_date:
            data_by_hour = prepare_pnvalue_hour_data(
                filter_params, view_types, pnvalue_types, base_radix)
            if data_by_hour is None:
                raise NoDataError(
                    "No hour data between %s - %s" % (begin_date, end_date))

            item_idx = 0
            for (view_type_idx, view_des) in view_types:
                if view_type_idx not in data_by_hour:
                    continue
                item = make_plot_item(data_by_hour[view_type_idx], \
                    pnvalue_types, item_idx, HOUR_XAXIS,
                    title, "%s %s" % (subtitle, view_des), ytitle)
                items.append(item)
                item_idx += 1
        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_pnvalue_daily_data(
                filter_params, days_region, view_types, 
                pnvalue_types, base_radix)
            if data_by_day is None:
                raise NoDataError(
                    "No daily data between %s - %s" % (begin_date, end_date))

            format_days_region = ["%s%s" %
                                  (i[5:7], i[8:10]) for i in days_region]
            item_idx = 0
            for (view_type_idx, view_des) in view_types:
                if view_type_idx not in data_by_day:
                    continue
                item = make_plot_item(data_by_day[view_type_idx], pnvalue_types,
                    item_idx, format_days_region, title, 
                    "%s %s" % (subtitle, view_des), ytitle)
                items.append(item)
                item_idx += 1

    except Exception, e:
        logger.info("query %s multiQos error: %s" % (str(table), e))

    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents'] = items
    if len(items) > 0:
        context['has_data'] = True

    logger.info("query %s multiQos, cost: %s" %
                (str(table), (current_time() - begin_time)))

    return context


@login_required
def show_fbuffer_time(request, dev=""):
    context = process_multi_plot(
        request, "fbuffer", "缓冲PN值", "", "单位：秒", VIEW_TYPES[1:], PNVALUES_LIST)
    do_mobile_support(request, dev, context)

    response = render_to_response('show_fbuffer_time.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_play_time(request, dev=""):
    context = process_multi_plot(
        request, "playtime", "播放时长PN值", "", "单位：分钟", VIEW_TYPES[1:], PNVALUES_LIST, 60)
    do_mobile_support(request, dev, context)
    response = render_to_response('show_play_time.html', context)
    set_default_values_to_cookie(response, context)

    return response
