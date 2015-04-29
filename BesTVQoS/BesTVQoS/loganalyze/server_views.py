# -*- coding: utf-8 -*-

import logging
import MySQLdb
from django.shortcuts import render_to_response
from django.db import connection
from common.views import HtmlTable
#from common.views import make_plot_item
from common.date_time_tool import today
from common.date_time_tool import current_time
from common.date_time_tool import get_days_region

logger = logging.getLogger("django.request")

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, xAlis, title, subtitle, ytitle1, ytitle2=""):
    item = {}
    item["index"] = item_idx
    item["title"] = title  # u"首次缓冲成功率"
    item["subtitle"] = subtitle  # u"全天24小时/全类型"
    item["y_title1"] = ytitle1  # u"成功率"
    item["y_title2"] = ytitle2  # u"成功率"
    item["xAxis"] = xAlis
    item["t_interval"] = 1
    if len(xAlis) > 30:
        item["t_interval"] = len(xAlis) / 30

    series = []
    for (i, j, desc) in keys:
        serie_item = '''{
            name: '%s',
            yAxis: %s,
            type: 'spline',
            data: [%s]
        }''' % (desc, j, ",".join(key_values[i]))
        series.append(serie_item)
    item["series"] = ",".join(series)

    return item

def show_server_list(request, dev=""):
    context = {}

    code_filter = request.GET.get("code_filter", "")
    #end_date = request.GET.get("end_date", str(today()))
    end_date = request.GET.get("end_date", "2015-04-28")

    table = HtmlTable()
    table.mtitle = u"服务器运行状况"
    table.mheader = [u"驻地", "IP", u"200占比(%)", u"记录数"]
    table.msub = []

    subs = [["江苏移动", "10.50.131.112", "89.3", "1000"],
            ["江苏移动", "10.50.131.9", "60.5", "500"]]

    table.msub = subs

    context['table'] = table
    context['default_date'] = end_date

    return render_to_response('show_server_list.html', context)


def prepare_hourly_ratio_history(ip, code, datum):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'test')
    cu = db.cursor()
    sql  = "select Hour, Ratio, Records from view_codeinfo "
    sql += "where IP='%s' and Date='%s' " % (ip, datum)
    sql += "and Code=%d" % (code)

    logger.debug("Daily Ratio SQL - %s" % sql)

    data_by_hour = {}
    if_has_data = False
    date_ratio = [0.0 for k in range(24)]
    date_delay = [0.0 for k in range(24)]

    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    for row in results:
        date_ratio[row[0]] = row[1]
        date_delay[row[0]] = row[2]
        if (row[0] + row[2]) > 0:
            if_has_data = True

    data_by_hour[0] = ['%s' % k for k in date_ratio]
    data_by_hour[1] = ['%s' % k for k in date_delay]

    db.close()

    if if_has_data == False:
        return None

    return data_by_hour


def prepare_daily_ratio_history(ip, code, begin_date, end_date):    
    
    return None


def get_ratio_history(ip, code, begin_date, end_date):
    keys = [(0, 0, u"%d占比" % code), (1, 1, u"记录数")]

    if begin_date == end_date:
        datas = prepare_hourly_ratio_history(ip, code, end_date)
        xalis = ["%d" % i for i in range(24)]
    else:
        datas = prepare_daily_ratio_history(ip, code, begin_date, end_date)
        days_region = get_days_region(begin_date, end_date)
        xalis = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
    
    if datas is None:
        raise NoDataError("No data between %s - %s" % (begin_date, end_date))

    item = make_plot_item(datas, keys, 0, xalis, (u"%d占比及记录数" % code), "", u"百分比(%)", u"记录数")

    return item


def prepare_hourly_delay_history(ip, code, datum):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'test')
    cu = db.cursor()

    data_by_hour = {}
    
    sql  = "SELECT P25, P50, P75, P90, P95, AvgTime, Hour From view_respdelayinfo "
    sql += "where IP='%s' and Date='%s' " % (ip, datum)
    sql += "and Code=%d" % (code)

    logger.debug("Daily Delay SQL - %s" % sql)

    display_data = {}
    data_count = 6
    for data_idx in range(data_count):
        display_data[data_idx] = ["0" for k in range(24)]

    if_has_data = False
    cu.execute(sql)
    results = cu.fetchall()
    for row in results:
        hour = row[6]
        for data_idx in range(data_count):
            display_data[data_idx][hour] = "%s" % row[data_idx]

            if row[data_idx] > 0:
                if_has_data = True

    if if_has_data:
        for data_idx in range(data_count):
            data_by_hour[data_idx] = display_data[data_idx]

    db.close()

    if len(data_by_hour) == 0:
        return None

    return data_by_hour


def get_delay_history(ip, code, begin_date, end_date):
    keys = [(0, 0, "P25"), (1, 0, "P50"), (2, 0, "P75"), (3, 0, "P90"), (4, 0, "P95")]

    if begin_date == end_date:
        datas = prepare_hourly_delay_history(ip, code, end_date)
        xalis = ["%d" % i for i in range(24)]
    else:
        datas = prepare_daily_delay_history(ip, code, begin_date, end_date)
        days_region = get_days_region(begin_date, end_date)
        xalis = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
    
    if datas is None:
        raise NoDataError("No data between %s - %s" % (begin_date, end_date))

    item = make_plot_item(datas, keys, 1, xalis, u"服务器响应时延", "", u"百分比(%)")

    return item


def show_server_detail(request, dev=""):
    context = {}

    server_ip = request.GET.get("ip", "Null")
    end_date = request.GET.get("end_date", str(today()))
    begin_date = request.GET.get("begin_date", end_date)

    try:
        items = []
        items_ratio = get_ratio_history(server_ip, 200, begin_date, end_date)
        items.append(items_ratio)

        items_delay = get_delay_history(server_ip, 200, begin_date, end_date)
        items.append(items_delay)

        context['contents'] = items
        if len(items) > 0:
            context['has_data'] = True
    except Exception, e:
        logger.debug(e)

    context["server_ip"] = server_ip
    context["default_begin_date"] = begin_date
    context["default_end_date"] = end_date

    return render_to_response('show_server_detail.html', context)