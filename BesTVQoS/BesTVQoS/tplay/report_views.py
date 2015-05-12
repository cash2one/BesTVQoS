# -*- coding: utf-8 -*-
import logging
import xlwt as xlwt
import MySQLdb

from django.http import HttpResponse
from django.shortcuts import render_to_response
from common.views import write_xls, write_remarks_to_xls, \
    get_report_filter_param_values, HtmlTable
from common.date_time_tool import current_time

ezxf=xlwt.easyxf

VIEW_TYPES = [
    (0, "总体"), (1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")]

logger = logging.getLogger("django.request")

#def write_xls(book, sheet, rowx, headings, data, heading_xf, data_xf):
#    for colx, value in enumerate(headings):
#        sheet.write(rowx, colx, value, heading_xf)

#    for row in data:
#        rowx+=1
#        for colx, value in enumerate(row):
#            sheet.write(rowx, colx, value, data_xf)

#    return rowx

#def write_remarks_to_xls(book, sheet, rowx, data, data_xf):
#    for value in data:
#        sheet.write(rowx, 0, value, data_xf)
#        rowx+=1

#    return rowx

def get_records_data(begin_date, end_date, beta_ver, master_ver):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()

    qos_data = []
    vers = []
    if len(beta_ver)>0:
        vers.append(beta_ver)
    if len(master_ver)>0:
        vers.append(master_ver)

    view_type = [1, 2, 3, 4] #(1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")
    for ver in vers:
        temp = []
        temp.append("%s"%(ver))
        total = 0
        for view in view_type:
            sql = "SELECT Records FROM playinfo WHERE DeviceType='%s' and \
                Date >= '%s' and Date <= '%s' and Hour=24 and ViewType=%d" % (
                    ver, begin_date, end_date, view)
            cursor.execute(sql)
            results = cursor.fetchall()
            record_sum = 0
            for row in results:
                record_sum += row[0]
            temp.append(record_sum)
            total += record_sum
        temp.append(total)
        qos_data.append(temp)

    mysql_db.close()
    return qos_data

def get_single_qos_data2(begin_date, end_date, beta_ver, master_ver):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()

    qos_data = []
    vers = []
    if len(beta_ver)>0:
        vers.append(beta_ver)
    if len(master_ver)>0:
        vers.append(master_ver)
    
    single_qos = ['fbuffer', 'fluency', 'fluency']
    qos_name = ['SucRatio', 'Fluency', 'PRatio']
    qos_desc = ['首次缓冲成功率', '一次不卡比例', '卡用户卡时间比']
    view_type = [1, 2, 3, 4]  #(1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")
    for index, qos in enumerate(qos_name):
        for ver in vers:
            temp = []
            temp.append("%s-%s"%(qos_desc[index], ver))
            for view in view_type:
                begin_time = current_time()                
                qos_sum = 0
                count = 0
                sql = "SELECT %s FROM %s WHERE DeviceType='%s' and Date >= '%s' \
                    and Date <= '%s' and Hour=24 and ViewType=%d" % (
                    qos, single_qos[index], ver, begin_date, end_date, view)
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    qos_sum += row[0]
                    count += 1
                avg = 0
                if count > 0:
                    avg = qos_sum/count
                temp.append(float("%.3f"%(avg)))
                logger.info("aggregate22 qos %s, count %d, cost: %s" 
                            %(qos, count, (current_time() - begin_time)))
            qos_data.append(temp)

    mysql_db.close()
    return qos_data

# p25, 50, 75, 90, 95, avg
def get_multi_qos_data(table, view_types, begin_date, end_date, beta_ver, master_ver, p95_exception_value, base_radis=1):
    mysql_db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = mysql_db.cursor()

    qos_data = []
    vers = []
    if len(beta_ver)>0:
        vers.append(beta_ver)
    if len(master_ver)>0:
        vers.append(master_ver)

    for (view, second) in view_types:
        for ver in vers:
            temp = [0 for i in range(7)]
            temp[0] = "%s-%s" % (ver, second)
            sql = "SELECT P25, P50, P75, P90, P95, AverageTime FROM %s WHERE \
                DeviceType='%s' and Date >= '%s' and Date <= '%s' \
                and Hour=24 and ViewType=%d" % (
                table, ver, begin_date, end_date, view)
            cursor.execute(sql)
            results = cursor.fetchall()
            count = 0
            for row in results:
                if row[4] < p95_exception_value:
                    continue
                for i in range(6):
                    temp[i+1] += row[i]
                count += 1

            if count > 0:
                for i in range(6):
                    temp[i+1] = temp[i+1]/count/base_radis

            qos_data.append(temp)
    mysql_db.close()
    return qos_data

def get_playtm_data(begin_date, end_date, beta_ver, master_ver):
    return get_multi_qos_data("playtime", VIEW_TYPES[1:4], begin_date, 
        end_date, beta_ver, master_ver, 1800, 60)

def get_fbuffer_data(begin_date, end_date, beta_ver, master_ver):
    return get_multi_qos_data("fbuffer", VIEW_TYPES[1:4], begin_date, 
        end_date, beta_ver, master_ver, 3)

def get_desc_for_daily_report(begin_date, end_date, beta_ver, master_ver=""):
    desc = [
        ['日期: %s - %s' % (begin_date, end_date)],
        ['%s -- %s' % ('首选版本', beta_ver)]
        ]
    if len(master_ver)>0:
        desc.append(['%s -- %s'%('对比版本', master_ver)])
    return desc

def generate_report(wb, begin_date, end_date, beta_ver, master_ver=""):
    begin_time = current_time()
    book = wb
    sheet = book.add_sheet("version-report")
    sheet.col(0).width=10000
    
    heading_xf = ezxf('borders: left thin, right thin, top thin, bottom thin; \
        font: bold on; pattern: pattern solid, fore_colour bright_green')
    data_xf = ezxf('borders: left thin, right thin, top thin, bottom thin; \
        font: name Arial')

    rowx = 0

    #
    # step 0: spec
    #
    spec_xf = ezxf('font: name Arial, colour Red')
    spec_data = get_desc_for_daily_report(begin_date, end_date, \
        beta_ver, master_ver)
    
    rowx = write_xls(book, sheet, rowx, [], spec_data, [], spec_xf)
    rowx += 2
    
    #
    # step 1: records
    #
    records_headings = ['记录数/版本', '点播', '回看', '直播', '连看', '总计']
    # prepare data
    records_data = get_records_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, records_headings, records_data, 
        heading_xf, data_xf)
    rowx += 2
    print "step 1: ", current_time() - begin_time
    #
    # step 2: single Qos
    #     
    single_qos_headings = ['单指标QoS/版本', '点播', '回看', '直播', '连看']
    single_qos_data = get_single_qos_data2(begin_date, end_date, beta_ver, 
        master_ver)
    rowx = write_xls(book, sheet, rowx, single_qos_headings, single_qos_data, 
        heading_xf, data_xf)
    rowx += 2
    print "step 2: ", current_time() - begin_time

    #
    # step 3: playtm
    #    
    playtm_headings = ['播放时长(分钟)', 'P25', 'P50', 'P75', 'P90', 'P95', '均值']
    playtm_data = get_playtm_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, playtm_headings, playtm_data, 
        heading_xf, data_xf)
    rowx += 2
    print "step 3: ", current_time() - begin_time
    
    #
    # step 4: fbuffer
    #    
    fbuffer_headings = ['首次缓冲时长(秒)', 'P25', 'P50', 'P75', 'P90', 'P95', '均值']
    fbuffer_data = get_fbuffer_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, fbuffer_headings, fbuffer_data, 
        heading_xf, data_xf)
    rowx += 2
    print "step 4: ", current_time() - begin_time
    
    #
    # step 5: remarks
    #    
    remark_xf = ezxf('font: name Arial, colour Red')
    remarks = ['备注: ', '一次不卡比例：无卡顿播放次数/加载成功的播放次数', '卡用户卡时间比：卡顿总时长/卡顿用户播放总时长',\
        '缓冲异常值过滤：如果P95<3秒，则认为数据有问题', '播放时长异常值过滤：如果P95小于30分钟，则认为数据有问题', \
        '多天报表的算均值：算均值可能存在差错']
    rowx = write_remarks_to_xls(book, sheet, rowx, remarks, remark_xf)
    rowx += 2
    print "step 4: ", current_time() - begin_time
    
    logger.info("generate_report:  %s - %s, cost: %s" %
                (begin_date, end_date, (current_time() - begin_time)))
    print begin_date, end_date, beta_ver, current_time() - begin_time

def pre_day_reporter(request, dev=""):
    (service_type, device_type, device_types, 
            version, versions, version2, versions2, begin_date, end_date) \
        = get_report_filter_param_values(request, "playinfo")
    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = ["All", "B2B", "B2C"]
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_version2'] = version2
    context['versions2'] = versions2
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['has_table'] = False
    response = render_to_response('show_daily_report.html', context)
    return response

def get_records_data_for_table(urls_suffix, begin_date, end_date, beta_ver, master_ver):
    datas = get_records_data(begin_date, end_date, beta_ver, master_ver)
    tables = []
    for i, data in enumerate(datas):
        item = {}
        item['click'] = True
        item['url'] = "show_playing_trend?%s" % (urls_suffix[i])
        item['data'] = data
        tables.append(item)
    return tables

def get_single_qos_data2_for_table(urls_suffix, begin_date, end_date, beta_ver, master_ver):
    datas = get_single_qos_data2(begin_date, end_date, beta_ver, master_ver)
    tables = []
    urls_prefix = ['show_fbuffer_sucratio?', 'show_fluency?', 
        'show_fluency_pratio?']
    for i, data in enumerate(datas):
        j = i
        if len(datas)==6:
            j /= 2
            i %= 2
        else:
            i = 0
        item = {}
        item['click'] = True
        item['url'] = "%s%s" % (urls_prefix[j], urls_suffix[i])
        item['data'] = data
        tables.append(item)
    return tables

def get_playtm_data_for_table(urls_suffix, begin_date, end_date, beta_ver, master_ver):
    datas = get_playtm_data(begin_date, end_date, beta_ver, master_ver)
    tables = []
    for i, data in enumerate(datas):
        if len(datas)==6:
            i %= 2
        else:
            i = 0
        item = {}
        item['click'] = True
        item['url'] = "show_play_time?%s" % (urls_suffix[i])
        item['data'] = data
        tables.append(item)
    return tables

def get_fbuffer_data_for_table(urls_suffix, begin_date, end_date, beta_ver, master_ver):
    datas = get_fbuffer_data(begin_date, end_date, beta_ver, master_ver)
    tables = []
    for i, data in enumerate(datas):
        if len(datas)==6:
            i %= 2
        else:
            i = 0
        item = {}
        item['click'] = True
        item['url'] = "show_fbuffer_time?%s" % (urls_suffix[i])
        item['data'] = data
        tables.append(item)
    return tables

def get_daily_report_tables(urls_suffix, begin_date, end_date, beta_ver, master_ver=""):
    tables = []
    # 0. date-ver table
    table = HtmlTable()
    table.mtitle = "records信息"
    table.mheader = ['日期-版本']
    table.msub = []
    descs = get_desc_for_daily_report(begin_date, end_date, 
        beta_ver, master_ver)
    for desc in descs:
        item = {}
        item['click'] = False
        item['url'] = '' 
        item['data'] = desc
        table.msub.append(item)
    tables.append(table)

    # 1. record table
    table = HtmlTable()
    table.mtitle = "日期版本信息"
    table.mheader = ['记录数/版本', '点播', '回看', '直播', '连看', '总计'] 
    table.msub = get_records_data_for_table(urls_suffix, begin_date, 
        end_date, beta_ver, master_ver)
    tables.append(table)

    # 2. single Qos table
    table = HtmlTable()
    table.mtitle = "SingleQos信息"
    table.mheader = ['单指标QoS/版本', '点播', '回看', '直播', '连看']
    table.msub = get_single_qos_data2_for_table(urls_suffix, 
        begin_date, end_date, beta_ver, master_ver)
    tables.append(table)

    # 3. playtm table
    table = HtmlTable()
    table.mtitle = "playtm信息"
    table.mheader = ['播放时长(分钟)', 'P25', 'P50', 'P75', 'P90', 'P95', '均值']
    table.msub = get_playtm_data_for_table(urls_suffix, 
        begin_date, end_date, beta_ver, master_ver)
    tables.append(table)

    # 4. fbuffer table
    table = HtmlTable()
    table.mtitle = "fbuffer信息"
    table.mheader = ['首次缓冲时长(秒)', 'P25', 'P50', 'P75', 'P90', 'P95', '均值']
    table.msub = get_fbuffer_data_for_table(urls_suffix, 
        begin_date, end_date, beta_ver, master_ver)
    tables.append(table)

    # 5. remarks table
    table = HtmlTable()
    table.mtitle = "备注信息"
    table.mheader = ['备注']
    table.msub = []
    datas = [
        ['点击表格可跳转到相应的Qos'],
        ['一次不卡比例：无卡顿播放次数/加载成功的播放次数'], ['卡用户卡时间比：卡顿总时长/卡顿用户播放总时长'],\
        ['缓冲异常值过滤：如果P95<3秒，则认为数据有问题'],
        ['播放时长异常值过滤：如果P95小于30分钟，则认为数据有问题'],
        ['多天报表的算均值：算均值可能存在差错']]
    for data in datas:
        item = {}
        item['click'] = False
        item['url'] = '' 
        item['data'] = data
        table.msub.append(item)
    
    tables.append(table)
    
    return tables

def get_version_version2(device_type, version, version2):
    if version != "All":
        version = '%s_%s' % (device_type, version) 
    else:
        version = device_type
    if version2 != "All":
        version2 = '%s_%s' % (device_type, version2) 
    else:
        version2 = device_type
    if version == version2:
        version2 = ""
    return (version, version2)

def display_daily_reporter(request, dev=""):
    (service_type, device_type, device_types, 
            version, versions, version2, versions2, begin_date, end_date) \
        = get_report_filter_param_values(request, "playinfo")
    context = {}
    context['default_service_type'] = service_type
    context['service_types'] = ["All", "B2B", "B2C"]
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_version2'] = version2
    context['versions2'] = versions2
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)

    urls_suffix = ['device_type=%s&version=%s&begin_date=%s&end_date=%s ' \
        % (device_type, version, begin_date, end_date), \
        'device_type=%s&version=%s&begin_date=%s&end_date=%s' \
        % (device_type, version2, begin_date, end_date),]
    (version, version2)=get_version_version2(device_type, version, version2)

    tables = get_daily_report_tables(urls_suffix, begin_date, end_date, 
        version, version2)
    context['has_table'] = True
    context['tables'] = tables

    response = render_to_response('show_daily_report.html', context)
    return response

def download_daily_reporter(request, dev=""):
    (service_type, device_type, device_types, version, versions, version2, \
        versions2, begin_date, end_date) = get_report_filter_param_values(request, "playinfo")

    (version, version2)=get_version_version2(device_type, version, version2)

    xlwt_wb = xlwt.Workbook()
    generate_report(xlwt_wb, begin_date, end_date, version, version2)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' \
        % (version, begin_date)
    xlwt_wb.save(response)
    return response

def day_reporter(request, dev=""):
    xlwt_wb = xlwt.Workbook()
    generate_report(xlwt_wb, "2015-04-23", "2015-04-23", "BesTV_Lite_A_2.6.4.9", 
        "BesTV_Lite_A_2.6.4.2")

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=day_report_%s.xls' \
        % ('2015-04-22')
    xlwt_wb.save(response)
    return response

def week_reporter(request, dev=""):
    xlwt_wb = xlwt.Workbook()
    generate_report(xlwt_wb, "2015-04-23", "2015-04-23", "BesTV_Lite_A_2.6.4.9", 
        "BesTV_Lite_A_2.6.4.2")

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=week_report_%s.xls'\
        % ('2015-04-22')
    xlwt_wb.save(response)
    return response