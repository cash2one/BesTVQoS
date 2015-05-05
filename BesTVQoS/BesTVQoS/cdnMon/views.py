# -*- coding: utf-8 -*-

import logging
import MySQLdb
import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection
from common.views import HtmlTable
from common.date_time_tool import get_day_of_day
from common.date_time_tool import current_time

logger = logging.getLogger("django.request")

def show_ms_error(request, dev=""):
    context = {}

    date = request.GET.get("date", str(get_day_of_day(-1)))

    table = HtmlTable()
    table.mtitle = u"ms_error信息"
    table.mheader = [u"响应码", "ClientIP", u"省份", u"运营商", 'ServerIP', u'省份', u'运营商', 'url']
    table.msub = []

    sql = "select Resp, ClientIP, ClientISP, ClientArea, ServIP, ServISP, ServArea, URL \
            from ms_error_info where Date='%s'" % date

    logger.debug("Server List SQL - %s" % sql)

    cu = connection.cursor()
    begin_time = current_time()
    cu.execute(sql)
    results = cu.fetchall()
    logger.info("execute sql:  %s, cost: %s" % (sql, (current_time() - begin_time)))
    subs = []
    for row in results:
        sub = []
        for i in range(7):
            sub.append(row[i])
        sub.append('''<a href="%s" target="_blank">%s</a>'''%(row[7], row[7]))
        subs.append(sub)

    table.msub = subs

    context['table'] = table
    context['default_date'] = date

    return render_to_response('show_ms_error.html', context)
