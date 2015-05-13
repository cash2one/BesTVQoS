# -*- coding: utf-8 -*-

import logging
import MySQLdb
import json
import xlwt as xlwt

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.db import connection
from common.views import HtmlTable
from common.views import write_xls
from common.views import write_remarks_to_xls
from common.date_time_tool import today
from common.date_time_tool import current_time
from common.date_time_tool import get_days_region
from common.date_time_tool import get_days_offset

logger = logging.getLogger("django.request")

business_types = ["ALL", "AAA", "EPG", "BSD", "PS"]


def make_plot_item2(key_values, keys, item_idx, xAlis, title, subtitle, ytitle1, interval=1, ytitle2=""):
    item = {}
    item["index"] = item_idx
    item["title"] = title
    item["subtitle"] = subtitle
    item["y_title1"] = ytitle1
    item["y_title2"] = ytitle2
    item["xAxis"] = xAlis
    item["t_interval"] = interval

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


def get_multidays_interval(days):
    intervals = [1, 1, 2, 3, 4, 4, 6, 6, 8, 8, 8, 8, 12]
    interval = 1
    if days < 12:
        interval = intervals[days]
    elif days < 24:
        interval = 12
    else:
        interval = int(days / 24) * 24

    return interval    


def get_server_list_table(business_type, datum):
    table = HtmlTable()
    table.mtitle = u"服务器运行状况"
    table.mheader = [u"驻地", u"业务类型", "IP", u"200占比(%)", u"记录数"]
    table.msub = []

    sql  = "select Area, ISP, Type, IP, 100*Ratio, Records from view_servers_status "
    sql += "where Date='%s'" % datum
    if business_type != business_types[0]:
        sql += " and Type='%s'" % business_type

    logger.debug("Server List SQL - %s" % sql)

    cu = connection.cursor()
    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    subs = []
    for row in results:
        sub = []
        sub.append("%s_%s" % (row[0], row[1]))
        sub.append("%s" % row[2])
        sub.append("%s" % row[3])
        sub.append("%.2f" % (float(row[4])))
        sub.append("%s" % row[5])
        subs.append(sub)

    table.msub = subs

    return table


#@login_required
def show_server_list(request, dev=""):
    context = {}

    business_type = request.GET.get("business_type", business_types[0])
    end_date = request.GET.get("date", str(today()))

    table = get_server_list_table(business_type, end_date)

    context['table'] = table
    context['default_date'] = end_date
    context['business_types'] = business_types
    context['default_business_type'] = business_type

    return render_to_response('show_server_list.html', context)


def append_to_excel(wb, table, sheet, row_idx):
    begin_time = current_time()

    sheet = wb.add_sheet(sheet)
    #sheet.col(0).width=3000
    #sheet.col(2).width=4000
    
    heading_xf=xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on; pattern: pattern solid, fore_colour bright_green')
    data_xf=xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: name Arial')
    spec_xf=xlwt.easyxf('font: name Arial, colour Red')

    row_idx = write_remarks_to_xls(wb, sheet, row_idx, [table.mtitle], spec_xf)
    row_idx += 1

    row_idx = write_xls(wb, sheet, row_idx, table.mheader, table.msub, heading_xf, data_xf)


#@login_required
def export_server_list(request, dev=""):
    business_type = request.GET.get("business_type", business_types[0])
    datum = request.GET.get("date", str(today()))

    table = get_server_list_table(business_type, datum)
    wb = xlwt.Workbook()
    append_to_excel(wb, table, "ServerList_%s" % datum, 0)
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=server_list_%s_%s.xls'%(datum, business_type)
    wb.save(response)

    return response


def prepare_hourly_ratio_history(ip, code, begin_date, end_date, xalis):
    data_by_hour = {}
    if_has_data = False
    data_count = len(xalis)

    cu = connection.cursor()

    # for ratio
    sql  = "select Date, Hour, 100*Ratio from view_codeinfo "
    sql += "where IP='%s' and Date>='%s' and Date<='%s' " % (ip, begin_date, end_date)
    sql += "and Hour<24 and Code=%d " % (code)

    logger.debug("Ratio SQL - %s" % sql)

    date_ratio = [0.0 for k in range(data_count)]

    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    for row in results:
        day_offset = get_days_offset(begin_date, str(row[0]))
        data_idx = 24 * day_offset + row[1]
        date_ratio[data_idx] = "%.2f" % float(row[2])
        if row[2] > 0:
            if_has_data = True

    data_by_hour[0] = ['%s' % k for k in date_ratio]

    # for Record
    sql  = "select Date, Hour, sum(Records) from view_codeinfo "
    sql += "where IP='%s' and Date>='%s' and Date<='%s' " % (ip, begin_date, end_date)
    sql += "and Hour<24 group by Date, Hour"

    logger.debug("Records SQL - %s" % sql)
    
    date_records = [0.0 for k in range(data_count)]

    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    for row in results:
        day_offset = get_days_offset(begin_date, str(row[0]))
        data_idx = 24 * day_offset + row[1]
        date_records[data_idx] = "%d" % row[2]
        if row[2] > 0:
            if_has_data = True

    data_by_hour[1] = ['%s' % k for k in date_records]

    if if_has_data == False:
        return None

    return data_by_hour


def get_ratio_history(ip, code, begin_date, end_date):
    keys = [(0, 0, u"%d占比" % code), (1, 1, u"记录数")]

    if begin_date == end_date:
        xalis = ["%d:00" % i for i in range(24)]
    else:
        days_region = get_days_region(begin_date, end_date)
        xalis_day = [i for i in days_region]
        xalis = []
        for d in xalis_day:
            xalis_hour = ["%s:00" % i for i in range(24)]
            xalis_hour[0] = d
            xalis += xalis_hour

    datas = prepare_hourly_ratio_history(ip, code, begin_date, end_date, xalis)
    if datas is None:
        raise NoDataError("No data between %s - %s" % (begin_date, end_date))

    interval = get_multidays_interval(len(xalis)/24)
    item = make_plot_item2(datas, keys, 0, xalis, (u"%d占比及记录数" % code), "", u"百分比(%)", interval, u"记录数")

    return item


def prepare_hourly_delay_history(ip, code, begin_date, end_date, xalis):
    data_count = len(xalis)
    series_count = 6

    cu = connection.cursor()

    data_by_hour = {}
    
    sql  = "SELECT P25, P50, P75, P90, P95, AvgTime, Date, Hour From view_reqdelayinfo "
    sql += "where IP='%s' and Date>='%s' and Date<='%s' " % (ip, begin_date, end_date)
    sql += "and Hour<24 and Code=%d" % (code)

    logger.debug("Delay SQL - %s" % sql)

    display_data = {}
    for serie_idx in range(series_count):
        display_data[serie_idx] = ["0" for k in range(data_count)]

    if_has_data = False
    cu.execute(sql)
    results = cu.fetchall()
    for row in results:
        day_offset = get_days_offset(begin_date, str(row[6]))
        data_idx = 24 * day_offset + row[7]
        for serie_idx in range(series_count):
            display_data[serie_idx][data_idx] = "%s" % row[serie_idx]

            if row[serie_idx] > 0:
                if_has_data = True

    if if_has_data:
        for serie_idx in range(series_count):
            data_by_hour[serie_idx] = display_data[serie_idx]

    if len(data_by_hour) == 0:
        return None

    return data_by_hour


def get_delay_history(ip, code, begin_date, end_date):
    keys = [(0, 0, "P25"), (1, 0, "P50"), (2, 0, "P75"), (3, 0, "P90"), (4, 0, "P95")]

    if begin_date == end_date:
        xalis = ["%d:00" % i for i in range(24)]
    else:
        days_region = get_days_region(begin_date, end_date)
        xalis_day = [i for i in days_region]
        xalis = []
        for d in xalis_day:
            xalis_hour = ["%s:00" % i for i in range(24)]
            xalis_hour[0] = d
            xalis += xalis_hour
    
    datas = prepare_hourly_delay_history(ip, code, begin_date, end_date, xalis)
    if datas is None:
        raise NoDataError("No data between %s - %s" % (begin_date, end_date))
    
    interval = get_multidays_interval(len(xalis)/24)
    item = make_plot_item2(datas, keys, 1, xalis, u"服务器响应时延", "", u"时延(ms)", interval)

    return item


def get_code_distribute(server_ip, begin_date, end_date):
    datas = []
    if_has_data = False

    sql  = "select Code, sum(Records) from view_codeinfo "
    sql += "where IP='%s' " % (server_ip)
    sql += "and Date>='%s' and Date<='%s' " % (begin_date, end_date)
    sql += "and Hour<24 group by Code"
    
    logger.debug("Code Distribute SQL - %s" % sql)
    
    cu = connection.cursor()

    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    for row in results:
        data_item = [('%s' % row[0]), int(row[1])]
        datas.append(data_item)
        if_has_data = True

    item = {}
    item["index"] = 0
    item["title"] = u"服务器响应状态码分布"

    key_values = [datas]

    keys = [(0, u"占比")]

    series = []
    for (i, desc) in keys:
        serie_item = '''{
            type: 'pie',
            name: '%s',
            data: %s
        }''' % (desc, json.dumps(key_values[i]))
        series.append(serie_item)

    item["series"] = ",".join(series)

    if if_has_data == False:
        return None

    return item


#@login_required
def show_server_detail(request, dev=""):
    context = {}
    
    business_type = request.GET.get("business_type", "ALL")
    server_ip = request.GET.get("server_ip", "Null")
    end_date = request.GET.get("end_date", str(today()))
    begin_date = request.GET.get("begin_date", end_date)
    server_ips = []

    try:
        items = []
        items_ratio = get_ratio_history(server_ip, 200, begin_date, end_date)
        items.append(items_ratio)

        items_delay = get_delay_history(server_ip, 200, begin_date, end_date)
        items.append(items_delay)

        context['contents'] = items
        if len(items) > 0:
            context['has_data'] = True

        items_pie = []
        items_code_pie = get_code_distribute(server_ip, begin_date, end_date)
        items_pie.append(items_code_pie)

        context['pie_contents'] = items_pie

        sql = "select IP from serverinfo "
        if business_type != 'ALL':
            sql += "where Type='%s'" % business_type
        logger.debug("Get IP SQL - %s" % sql)
    
        cu = connection.cursor()
        
        cu.execute(sql)

        results = cu.fetchall()
        for row in results:
            server_ips.append(str(row[0]))

    except Exception, e:
        logger.debug(e)
        
    context['business_types'] = business_types
    context['default_business_type'] = business_type
    context["server_ips"] = server_ips
    context["default_server_ip"] = server_ip
    context["default_begin_date"] = begin_date
    context["default_end_date"] = end_date

    return render_to_response('show_server_detail.html', context)


#@login_required
def get_server_url_distribute(request, dev=""):
    url_distribute = {}
    try:
        server_ip = request.GET.get('server_ip')
        begin_date = request.GET.get('begin_date')
        end_date = request.GET.get('end_date')
        code = request.GET.get('code')

        url_distribute["mtitle"] = u"Code：%s 对应的URL访问分布情况" % code
        url_distribute["mheader"] = ["URL", "Records", "Ratio(%)"]
        url_distribute["msub"] = []

        # get count of all url records
        sql  = "select sum(Records) from view_urlinfo "
        sql += "where IP='%s' and Code=%s " % (server_ip, code)
        sql += "and Date>='%s' and Date<='%s' " % (begin_date, end_date)
        sql += "and Hour<24 and URL!='all' and Records>0"        
        logger.debug("Count URL SQL - %s" % sql)
    
        cu = connection.cursor()

        begin_time = current_time()
        cu.execute(sql)
        results = cu.fetchall()
        logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
        total_records = 0
        for row in results:
            if not row[0]:
                log  = "There are no URL records of Code %s on Server %s " % (code, server_ip)
                log += "between %s and %s" % (begin_date, end_date)
                raise Exception(log)
            total_records = int(row[0])

        # get count of all url records
        sql  = "select URL, sum(Records), 100*sum(Records)/%s " % (total_records)
        sql += "from view_urlinfo where IP='%s' and Code=%s " % (server_ip, code)
        sql += "and Date>='%s' and Date<='%s' " % (begin_date, end_date)
        sql += "and Hour<24 and URL!='all' and Records>0 "
        sql += "group by URL order by Records desc"        
        logger.debug("URL Distribute SQL - %s" % sql)

        begin_time = current_time()
        cu.execute(sql)
        results = cu.fetchall()
        logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))

        for row in results:
            try:
                sub = ["%s" % col for col in row]
                url_distribute["msub"].append(sub)
            except Exception, e:
                logger.debug(e)

    except Exception, e:
        logger.debug(e)
        url_distribute["mheader"] = []

    respStr = json.dumps({"url_distribute": url_distribute})
    return HttpResponse(respStr, content_type="text/json")


#@login_required
def get_ip_list(request, dev=""):
    business_type = request.GET.get("business_type", "ALL")
    server_ips = []
    try:
        sql = "select IP from serverinfo "
        if business_type != 'ALL':
            sql += "where Type='%s'" % business_type
        logger.debug("Get IP SQL - %s" % sql)
    
        cu = connection.cursor()
        
        cu.execute(sql)

        results = cu.fetchall()
        for row in results:
            server_ips.append(str(row[0]))
    except Exception, e:
        logger.debug(e)
    
    respStr = json.dumps({"server_ips": server_ips})

    return HttpResponse(respStr, content_type="text/json")