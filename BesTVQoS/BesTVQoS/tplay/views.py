# -*- coding: utf-8 -*-

# import json
import logging
import time

from django.shortcuts import render_to_response
from django.db import connection
from django import forms
from common.mobile import do_mobile_support
from tplay.models import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]


class HtmlTable:
    mtitle = "title"
    mheader = ["header"]
    mysub = [['sub1'], ['sub2']]


class DateForm(forms.Form):
    service_type = forms.CharField()
    date = forms.CharField()
    min_rec = forms.CharField()


class PlayProfile:

    def __init__(self, request):
        self.service_type = "All"
        self.date = time.strftime(
            '%Y-%m-%d', time.localtime(time.time() - 86400))
        self.min_rec = 0

        self.common_filter = ""
        self.service_type_filter = ""
        self.date_filter = ""
        self.min_rec_filter = ""

        self.read_date_form(request)

        self.cu = connection.cursor()

    def read_date_form(self, request):
        if(request.method == 'GET'):
            date_form = DateForm(request.GET)
            if date_form.is_valid():
                self.service_type = date_form.cleaned_data['service_type']
                self.date = date_form.cleaned_data['date']
                self.min_rec = date_form.cleaned_data['min_rec']

        self.get_common_filter()

    def get_common_filter(self):
        self.date_filter = " Date = '%s'" % (self.date)

        if (self.service_type == "All"):
            self.service_type_filter = ""
        else:
            self.service_type_filter = " and ServiceType = '%s' " % (
                self.service_type)

        self.min_rec_filter = " and Records >= %s" % (self.min_rec)

        self.common_filter = self.date_filter + self.service_type_filter


def show_playing_daily(request, dev=""):
    play_profile = PlayProfile(request)

    filter = "from playprofile where %s" % (play_profile.common_filter)
    sql_command = "select sum(Records), sum(Users) %s" % (filter)
    logger.debug("SQL %s" % sql_command)
    play_profile.cu.execute(sql_command)

    context = {}
    table = HtmlTable()
    table.mtitle = "%s 用户播放统计信息" % play_profile.date.encode('utf-8')
    table.mheader = [
        "服务类型", "设备类型", "播放数", '播放百分比%', '用户数', '用户百分比%', '人均播放时间', '人均播放次数']
    table.msub = []
    subs = []

    records_total = 0
    users_total = 0
    for item in play_profile.cu.fetchall():
        if item[0] and item[1]:
            records_total = int(item[0])
            users_total = int(item[1])

    if records_total == 0 or users_total == 0:
        logger.error("Unexpected Value: records_total: %d, users_total: %d" % (
            records_total, users_total))
    else:
        filter = filter + play_profile.min_rec_filter
        sql_command = "select ServiceType, DeviceType, Records, Users, \
            AverageTime, (Records/Users) %s" % (filter)
        logger.debug("SQL %s" % sql_command)
        play_profile.cu.execute(sql_command)

        for item in play_profile.cu.fetchall():
            sub = []
            sub.append(item[0])
            sub.append(item[1])
            sub.append(item[2])
            sub.append(round(100.0 * item[2] / records_total, 2))
            sub.append(item[3])
            sub.append(round(100.0 * item[3] / users_total, 2))
            sub.append(item[4])
            sub.append(int(float(item[5])))
            subs.append(sub)
            table.msub.append(sub)

    context['table'] = table
    context['default_date'] = play_profile.date
    context['default_min_rec'] = play_profile.min_rec
    context['default_service_type'] = play_profile.service_type
    context['service_types'] = SERVICE_TYPES

    do_mobile_support(request, dev, context)

    return render_to_response('show_playing_daily.html', context)


def show_playing_trend(request, dev=""):
    context = {}
    context['default_service_type'] = "All"
    context['service_types'] = SERVICE_TYPES
    context['default_service_type'] = "BesTV_OS_ABC_1.0.1"
    context['device_types'] = ['BesTV_OS_ABC_1.0.1', 'BesTV_OS_ABC_1.0.2']
    context['default_begin_date'] = "2015-03-24"
    context['default_end_date'] = "2015-03-24"

    do_mobile_support(request, dev, context)

    return render_to_response('show_playing_trend.html', context)
