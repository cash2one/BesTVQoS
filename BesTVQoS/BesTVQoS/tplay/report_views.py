# -*- coding: utf-8 -*-
import logging
import xlwt as xlwt
import MySQLdb

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db.models import Count, Min, Sum, Avg
from tplay.models import *
from common.mobile import do_mobile_support
from common.views import *
from common.date_time_tool import *

ezxf=xlwt.easyxf

VIEW_TYPES = [
    (0, u"总体"), (1, u"点播"), (2, u"回看"), (3, u"直播"), (4, u"连看"), (5, u"未知")]

logger = logging.getLogger("django.request")

def write_xls(book, sheet, rowx, headings, data, heading_xf, data_xf):
    for colx, value in enumerate(headings):
        sheet.write(rowx, colx, value, heading_xf)

    for row in data:
        rowx+=1
        for colx, value in enumerate(row):
            sheet.write(rowx, colx, value, data_xf)

    return rowx

def write_remarks_to_xls(book, sheet, rowx, data, data_xf):
    for value in data:
        sheet.write(rowx, 0, value, data_xf)
        rowx+=1

    return rowx

def get_records_data(begin_date, end_date, beta_ver, master_ver):
    return [
        ['2.6.4.9', 1000, 1000, 500, 500, 3000],
        ['2.6.4.2', 3000, 3000, 1000, 1000, 8000]
        ]

def get_single_qos_data2(begin_date, end_date, beta_ver, master_ver):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = db.cursor()

    qos_data=[]
    vers=[]
    if len(beta_ver)>0:
        vers.append(beta_ver)
    if len(master_ver)>0:
        vers.append(master_ver)
    
    single_qos=['fbuffer', 'fluency', 'fluency']
    qos_name=['SucRatio', 'Fluency', 'PRatio']
    qos_desc=[u'首次缓冲成功率', u'一次不卡比例', u'卡用户卡时间比']
    view_type=[1, 2, 3, 4]  #(1, u"点播"), (2, u"回看"), (3, u"直播"), (4, u"连看"), (5, u"未知")
    for index, qos in enumerate(qos_name):
        for ver in vers:
            temp=[]
            temp.append(u"%s-%s"%(qos_desc[index], ver))
            for view in view_type:
                begin_time = current_time()                
                sum=0
                count=0
                sql="SELECT %s FROM %s WHERE DeviceType='%s' and Date >= '%s' and Date <= '%s' and Hour=24 and ViewType='%s'"%(
                    qos, single_qos[index], ver, begin_date, end_date, view)
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    sum += row[0]
                    count+=1
                avg=0
                if count>1:
                    avg=sum/count
                temp.append(float("%.3f"%(avg)))
                logger.info("aggregate22 qos %s, count %d, cost: %s" 
                            %(qos, count, (current_time() - begin_time)))
            qos_data.append(temp)

    db.close()
    return qos_data

# p25, 50, 75, 90, 95, avg
def get_multi_qos_data(table, view_types, begin_date, end_date, beta_ver, master_ver):
    db = MySQLdb.connect('localhost', 'root', 'funshion', 'BesTVQoS')
    cursor = db.cursor()

    qos_data=[]
    vers=[]
    if len(beta_ver)>0:
        vers.append(beta_ver)
    if len(master_ver)>0:
        vers.append(master_ver)

    for (view, second) in view_types:
        for ver in vers:
            temp=[0 for i in range(7)]
            temp[0]=u"%s-%s"%(ver, second)
            sql="SELECT P25, P50, P75, P90, P95, AverageTime FROM %s WHERE DeviceType='%s' and Date >= '%s' and Date <= '%s' and Hour=24 and ViewType='%s'"%(
                    table, ver, begin_date, end_date, view)
            cursor.execute(sql)
            results = cursor.fetchall()
            count=0
            for row in results:
                count+=1
                for i in range(6):
                    temp[i+1]+=row[i]

            if count>1:
                for i in range(6):
                    temp[i+1]/=count

            qos_data.append(temp)
    db.close()
    return qos_data

def get_playtm_data(begin_date, end_date, beta_ver, master_ver):
    return get_multi_qos_data("playtime", VIEW_TYPES[1:4], begin_date, end_date, beta_ver, master_ver)

def get_fbuffer_data(begin_date, end_date, beta_ver, master_ver):
    return get_multi_qos_data("fbuffer", VIEW_TYPES[1:4], begin_date, end_date, beta_ver, master_ver)

def generate_report(wb, begin_date, end_date, beta_ver, master_ver=""):
    begin_time = current_time()
    book = wb
    sheet = book.add_sheet("version-report")
    sheet.col(0).width=10000
    
    heading_xf=ezxf('borders: left thin, right thin, top thin, bottom thin; font: bold on; pattern: pattern solid, fore_colour bright_green')
    data_xf=ezxf('borders: left thin, right thin, top thin, bottom thin; font: name Arial')

    rowx=0

    #
    # step 0: spec
    #
    spec_xf=ezxf('font: name Arial, colour Red')
    spec_data=[
        [u'日期: %s'%begin_date],
        [u'%s -- %s'%(beta_ver, u'公测版')]
        ]
    if len(master_ver)>0:
        spec_data.append([u'%s -- %s'%(master_ver, u'正式版')])
    
    rowx=write_xls(book, sheet, rowx, [], spec_data, [], spec_xf)
    rowx+=2
    
    #
    # step 1: records
    #
    records_headings=[u'记录数/版本', u'点播', u'回看', u'直播', u'连看', u'总计']
    # prepare data
    records_data=get_records_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, records_headings, records_data, heading_xf, data_xf)
    rowx+=2
    print "step 1: ", current_time() - begin_time
    #
    # step 2: single Qos
    #     
    single_qos_headings=[u'一次不卡比例/版本', u'点播', u'回看', u'直播', u'连看']
    single_qos_data=get_single_qos_data2(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, single_qos_headings, single_qos_data, heading_xf, data_xf)
    rowx+=2
    print "step 2: ", current_time() - begin_time

    #
    # step 3: playtm
    #    
    playtm_headings=[u'播放时长(分钟)', 'P25', 'P50', 'P75', 'P90', 'P95', u'均值']
    playtm_data=get_playtm_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, playtm_headings, playtm_data, heading_xf, data_xf)
    rowx+=2
    print "step 3: ", current_time() - begin_time
    
    #
    # step 4: fbuffer
    #    
    fbuffer_headings=[u'首次缓冲时长', 'P25', 'P50', 'P75', 'P90', 'P95', u'均值']
    fbuffer_data=get_fbuffer_data(begin_date, end_date, beta_ver, master_ver)
    rowx = write_xls(book, sheet, rowx, fbuffer_headings, fbuffer_data, heading_xf, data_xf)
    rowx+=2
    print "step 4: ", current_time() - begin_time
    
    #
    # step 5: remarks
    #    
    remark_xf=ezxf('font: name Arial, colour Red')
    remarks=[u'备注: ', u'一次不卡比例：无卡顿播放次数/加载成功的播放次数', u'卡用户卡时间比：卡顿总时长/卡顿用户播放总时长']
    rowx=write_remarks_to_xls(book, sheet, rowx, remarks, remark_xf)
    rowx+=2
    print "step 4: ", current_time() - begin_time
    
    logger.info("generate_report:  %s - %s, cost: %s" %
                (begin_date, end_date, (current_time() - begin_time)))
    print begin_date, end_date, beta_ver, current_time() - begin_time

def day_reporter(request, dev=""):
    wb = xlwt.Workbook()
    generate_report(wb, "2015-04-23", "2015-04-23", "BesTV_Lite_A_2.6.4.9", "BesTV_Lite_A_2.6.4.2")

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=day_report_%s.xls'%('2015-04-22')
    wb.save(response)
    return response

def week_reporter(request, dev=""):
    wb = xlwt.Workbook()
    generate_report(wb, "2015-04-23", "2015-04-23", "BesTV_Lite_A_2.6.4.9", "BesTV_Lite_A_2.6.4.2")

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=week_report_%s.xls'%('2015-04-22')
    wb.save(response)
    return response