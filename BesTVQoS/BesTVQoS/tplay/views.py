# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from datetime import timedelta

from django.shortcuts import render_to_response
from django.db import connection
from common.date_time_tool import *
from common.mobile import do_mobile_support
from common.views import *
from fbuffer_views import process_single_Qos
from tplay.models import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]

# VIEW_TYPES = [0, 1, 2, 3, 4, 5]
# VIEW_TYPES_DES = {
#     0: u"总计", 1: u"点播", 2: u"回看", 3: u"直播", 4: u"连看", 5: u"未知"}
VIEW_TYPES = [
    (0, u"总体"), (1, u"点播"), (2, u"回看"), (3, u"直播"), (4, u"连看"), (5, u"未知")]


def make_chart_item(key_values, item_idx, title, subtitle, y_title, xAlis):
    begin_time = current_time()
    item = {}
    item["index"] = item_idx
    item["title"] = title
    item["subtitle"] = subtitle
    item["y_title"] = y_title
    item["xAxis"] = xAlis
    item["t_interval"] = 1

    try:
        series = []
        for (i, desc) in VIEW_TYPES:
            serie_item = '''{
                name: '%s',
                yAxis: 0,
                type: 'spline',
                data: [%s]
            }''' % (desc, ",".join(key_values[i]))
            series.append(serie_item)
    except:
        logger.error("make_chart_item() failed with args: %s" %
                     (",".join(key_values[i])))

    item["series"] = ",".join(series)
    logger.debug("make_chart_item() cost %s" % (current_time() - begin_time))

    return item


class HtmlTable:
    mtitle = "title"
    mheader = ["header"]
    mysub = [['sub1'], ['sub2']]


class PlayInfo:

    def __init__(self, request):
        self.profile_exclude = " and DeviceType like '%.%'"
        self.service_type = "All"
        self.end_date = str(today())
        self.begin_date = self.end_date
        self.device_type = ""
        self.device_types = []
        self.min_rec = 0

        self.common_filter = ""
        self.service_type_filter = ""
        self.device_type_filter = ""
        self.date_filter = ""

        self.cu = connection.cursor()

    def read_filter_profile_form(self, request):
        if(request.method == 'GET'):
            self.service_type = request.GET.get('service_type', 'All')
            self.end_date = request.GET.get('date', self.end_date)
            self.begin_date = self.end_date
            self.min_rec = request.GET.get('min_rec', 0)

        self.get_common_filter()

    def read_filter_group_form(self, request):
        if(request.method == 'GET'):
            filters_map = get_default_values_from_cookie(request)
            self.service_type = request.GET.get(
                "service_type", filters_map["st"])
            self.device_type = request.GET.get(
                "device_type", filters_map["dt"])
            self.begin_date = request.GET.get(
                "begin_date", filters_map["begin"])
            self.end_date = request.GET.get("end_date", filters_map["end"])

        self.device_types = get_device_types1(
            "playinfo", self.service_type, self.begin_date,
            self.end_date, self.cu)

        if len(self.device_types) == 0:
            self.device_types.append("")

        if self.device_type == '':
            self.device_type = self.device_types[0]

        self.get_common_filter()

    def get_common_filter(self):
        self.date_filter = " Date >= '%s' and Date <= '%s'" % (
            self.begin_date, self.end_date)

        if (self.service_type != "All"):
            self.service_type_filter = " and ServiceType = '%s' " % (
                self.service_type)
        else:
            self.service_type_filter = ""

        if (self.device_type != ""):
            self.device_type_filter = " and DeviceType = '%s'" % (
                self.device_type)

        self.min_rec_filter = " and Records >= %s" % (self.min_rec)

        self.common_filter = self.date_filter + self.service_type_filter

    def get_playinfo_item(self, item_index):
        begin_time = current_time()

        x_axis = []
        y_axises = {}

        if self.begin_date == self.end_date:
            '''24 hours view'''
            fn_get_sql_cmd = self.get_hourly_sql_command
            for m in range(0, 24):
                x_axis.append('%s' % m)
        else:
            '''multidays view'''
            fn_get_sql_cmd = self.get_daily_sql_command
            tmp_end_date = datetime.strptime(
                self.end_date, '%Y-%m-%d')
            tmp_begin_date = datetime.strptime(
                self.begin_date, '%Y-%m-%d')
            for i in range((tmp_end_date - tmp_begin_date).days + 1):
                day = tmp_begin_date + timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                x_axis.append("%s" % day_str)

        for (vt, desc) in VIEW_TYPES:
            y_axise = []
            for x in x_axis:
                sql_command = fn_get_sql_cmd(x, vt)
                self.cu.execute(sql_command)

                records = '0'
                for item in self.cu.fetchall():
                    if item[0]:
                        records = '%d' % (item[0])
                y_axise.append(records)

            y_axises[vt] = y_axise

        time_cost = current_time() - begin_time
        logger.debug(
            "get_playinfo_item() exlude make_chart_item cost: %s" % (time_cost))

        return make_chart_item(y_axises, item_index, u'用户观看量',
                               u'', u'观看量', x_axis)

    def get_daily_sql_command(self, date, view_type):
        sql_command = "select sum(Records) from playinfo where Date = '%s'" % (
            date)
        sql_command += self.service_type_filter
        sql_command += self.device_type_filter
        sql_command += " and Hour = 24"
        if view_type != 0:
            sql_command += " and ViewType = '%s'" % (view_type)

        return sql_command

    def get_hourly_sql_command(self, hour, view_type):
        sql_command = "select sum(Records) from playinfo where %s" % (
            self.date_filter)
        sql_command += self.service_type_filter
        sql_command += self.device_type_filter
        sql_command += " and Hour = %s" % (hour)
        if view_type != 0:
            sql_command += " and ViewType = '%s'" % (view_type)

        return sql_command


def get_play_info_today(context, playinfo):
    table = HtmlTable()
    table.mtitle = "%s 用户播放统计信息（每小时更新）" % playinfo.end_date.encode('utf-8')
    table.mheader = ["服务类型", "设备类型", "播放数", '播放百分比%']
    table.msub = []
    subs = []
    if playinfo.end_date != str(today()):
        return table

    filters = "from playinfo where %s" % (playinfo.common_filter)
    sql_command = "select sum(Records) %s" % (filters)
    sql_command += playinfo.profile_exclude
    playinfo.cu.execute(sql_command)

    records_total = 0
    for item in playinfo.cu.fetchall():
        if item[0]:
            records_total = int(item[0])

    if records_total == 0:
        logger.error("Unexpected Value: records_total: %d" % (records_total))
    else:
        filters = filters + playinfo.min_rec_filter
        sql_command = "select ServiceType, DeviceType, sum(Records) %s" % (
            filters)
        sql_command += playinfo.profile_exclude
        sql_command += " group by DeviceType order by sum(Records) desc"
        playinfo.cu.execute(sql_command)

        for item in playinfo.cu.fetchall():
            sub = []
            sub.append(item[0])
            sub.append(item[1])
            sub.append(item[2])
            sub.append(round(100.0 * float(item[2]) / records_total, 2))
            subs.append(sub)
            table.msub.append(sub)

    return table


def get_play_profile_history(context, play_profile):
    table = HtmlTable()
    filters = "from playprofile where %s" % (play_profile.common_filter)
    sql_command = "select sum(Records), sum(Users) %s" % (filters)
    sql_command += play_profile.profile_exclude
    play_profile.cu.execute(sql_command)

    table.mtitle = "%s 用户播放统计信息" % play_profile.end_date.encode('utf-8')
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
        filters = filters + play_profile.min_rec_filter
        sql_command = "select ServiceType, DeviceType, Records, Users, \
            AverageTime, (Records/Users) %s" % (filters)
        sql_command += play_profile.profile_exclude
        sql_command += " order by Records desc"
        play_profile.cu.execute(sql_command)

        for item in play_profile.cu.fetchall():
            sub = []
            sub.append(item[0])
            sub.append(item[1])
            sub.append(item[2])
            sub.append(round(100.0 * float(item[2]) / records_total, 2))
            sub.append(item[3])
            sub.append(round(100.0 * float(item[3]) / users_total, 2))
            sub.append(item[4])
            if item[5] is None:
                sub.append(0)
            else:
                sub.append(int(float(item[5])))
            subs.append(sub)
            table.msub.append(sub)

    return table


def show_playing_daily(request, dev=""):
    context = {}
    table = HtmlTable()

    play_profile = PlayInfo(request)
    play_profile.read_filter_profile_form(request)

    if play_profile.end_date == str(today()):
        table = get_play_info_today(context, play_profile)
    else:
        table = get_play_profile_history(context, play_profile)

    context['table'] = table
    context['default_date'] = play_profile.end_date
    context['default_min_rec'] = play_profile.min_rec
    context['default_service_type'] = play_profile.service_type
    context['service_types'] = SERVICE_TYPES

    do_mobile_support(request, dev, context)

    return render_to_response('show_playing_daily.html', context)


def show_playing_trend(request, dev=""):
    context = process_single_Qos(
        request, BestvPlayinfo, "Records", u"用户观看量",
        u"", u"观看量", VIEW_TYPES, True, 1)

    do_mobile_support(request, dev, context)

    response = render_to_response('show_playing_trend.html', context)

    set_default_values_to_cookie(response, context)

    return response
