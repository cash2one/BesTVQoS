# -*- coding: utf-8 -*-

from common.views import *
from common.date_time_tool import *
from tplay.functions import process_single_qos, get_device_types, get_versions, process_multi_plot
from tplay.models import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]
VIEW_TYPES = [(0, "总体"), (1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")]
PN_LIST = [("P25", "P25"), ("P50", "P50"), ("P75", "P75"),
           ("P90", "P90"), ("P95", "P95"), ("AverageTime", "AVG")]

class PlayInfo:
    def __init__(self, request):
        self.profile_exclude = " and DeviceType like '%\.%'"
        self.service_type = "All"
        self.end_date = str(today())
        self.begin_date = self.end_date
        self.device_type = ""
        self.device_types = []
        self.version = "All"
        self.versions = ["All"]
        self.min_rec = 0

        self.common_filter = ""
        self.service_type_filter = ""
        self.device_type_filter = ""
        self.date_filter = ""
        self.min_rec_filter = ""

        self.cu = connection.cursor()

    def read_filter_profile_form(self, request):
        if request.method == 'GET':
            self.service_type = request.GET.get('service_type', 'All')
            self.end_date = request.GET.get('date', self.end_date)
            self.begin_date = self.end_date
            self.min_rec = request.GET.get('min_rec', 0)

        self.get_common_filter()

    def get_common_filter(self):
        self.date_filter = " Date >= '%s' and Date <= '%s'" % (
            self.begin_date, self.end_date)

        if self.service_type != "All":
            self.service_type_filter = " and ServiceType = '%s' " % (
                self.service_type)
        else:
            self.service_type_filter = ""

        if self.device_type != "":
            self.device_type_filter = " and DeviceType = '%s'" % (
                self.device_type)

        self.min_rec_filter = " and Records >= %s" % (self.min_rec)

        self.common_filter = self.date_filter + self.service_type_filter


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
    logger.debug("get records_total SQL: %s" % sql_command)
    begin_time = current_time()
    playinfo.cu.execute(sql_command)

    records_total = 0
    for item in playinfo.cu.fetchall():
        if item[0]:
            records_total = int(item[0])

    end_time = current_time()
    logger.debug("get records_total from MySql cost %ss" %
                 (end_time - begin_time))

    if records_total == 0:
        logger.error("Unexpected Value: records_total: %d" % (records_total))
    else:
        filters = filters + playinfo.min_rec_filter
        sql_command = "select ServiceType, DeviceType, sum(Records) %s" % (
            filters)
        sql_command += playinfo.profile_exclude
        sql_command += " group by ServiceType, DeviceType order by sum(Records) desc"
        logger.debug("SQL: %s" % sql_command)

        begin_time = current_time()
        playinfo.cu.execute(sql_command)

        for item in playinfo.cu.fetchall():
            sub = list()
            sub.append(item[0])
            sub.append(item[1])
            sub.append(item[2])
            sub.append(round(100.0 * float(item[2]) / records_total, 2))
            subs.append(sub)
            table.msub.append(sub)

        end_time = current_time()
        logger.debug("get datas from MySql cost %ss" % (end_time - begin_time))

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
            AverageTime, (Records/Users) %s" % filters
        sql_command += play_profile.profile_exclude
        sql_command += " order by Records desc"
        play_profile.cu.execute(sql_command)

        for item in play_profile.cu.fetchall():
            sub = list()
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


@login_required
def show_playing_daily(request):
    context = {}

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

    return render_to_response('show_playing_daily.html', context)


@login_required
def show_playing_trend(request):
    context = process_single_qos(request, BestvPlayinfo, "Records", u"用户观看量",
                                 u"", u"观看量", VIEW_TYPES, True, 1)
    response = render_to_response('show_playing_trend.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_play_time(request):
    context = process_multi_plot(request, BestvPlaytime, "播放时长PN值", "",
                                 "单位：分钟", VIEW_TYPES[1:], PN_LIST, 60)
    response = render_to_response('show_play_time.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fbuffer_sucratio(request):
    context = process_single_qos(request, BestvFbuffer, "SucRatio", "首次缓冲成功率",
                                 "加载成功的播放次数/播放总次数", "成功率(%)", VIEW_TYPES[1:], True, 100)
    response = render_to_response('show_fbuffer_sucratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency(request):
    context = process_single_qos(request, BestvFluency, "Fluency", "一次不卡比例",
                                 "无卡顿播放次数/加载成功的播放次数", "百分比(%)", VIEW_TYPES[1:], True, 100)
    response = render_to_response('show_fluency.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_pratio(request):
    context = process_single_qos(request, BestvFluency, "PRatio", "卡用户卡时间比",
                                 "卡顿总时长/卡顿用户播放总时长", "百分比(%)", VIEW_TYPES[1:], True, 100)
    response = render_to_response('show_fluency_pratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_allpratio(request):
    context = process_single_qos(request, BestvFluency, "AllPRatio", "所有用户卡时间比",
                                 "卡顿总时长/所有用户播放总时长", "百分比(%)", VIEW_TYPES[1:], True, 100)
    response = render_to_response('show_fluency_allpratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fluency_avgcount(request):
    context = process_single_qos(request, BestvFluency, "AvgCount", "卡顿播放平均卡次数",
                                 "卡顿总次数/卡顿播放数", "次数", VIEW_TYPES[1:], True)
    response = render_to_response('show_fluency_avgcount.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_3sratio(request):
    context = process_single_qos(request, Bestv3SRatio, "Ratio", "3秒起播占比",
                                 "3秒内加载成功的播放次数/播放总次数", "百分比(%）", VIEW_TYPES[0:1], False, 100)
    
    response = render_to_response('show_3sratio.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_avg_pcount(request):
    context = process_single_qos(request, BestvAvgPchoke, "AvgCount", "每小时播放卡顿平均次数",
                                 "卡顿次数/卡顿用户播放总时长（小时）", "次数", VIEW_TYPES[0:1], False)
    
    response = render_to_response('show_avg_pcount.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_avg_ptime(request):
    context = process_single_qos(request, BestvAvgPchoke, "AvgTime", "每小时播放卡顿平均时长",
                                 "卡顿总时长（秒）/卡顿用户播放总时长（小时）", "秒", VIEW_TYPES[0:1], False)
    response = render_to_response('show_avg_ptime.html', context)
    set_default_values_to_cookie(response, context)

    return response


@login_required
def show_fbuffer_time(request):
    context = process_multi_plot(request, BestvFbuffer, "缓冲PN值", "", "单位：秒", VIEW_TYPES[1:], PN_LIST)
    response = render_to_response('show_fbuffer_time.html', context)
    set_default_values_to_cookie(response, context)

    return response


def get_device_type(request):
    service_type = request.GET.get('service_type')
    begin_date = request.GET.get('begin_date')
    end_date = request.GET.get('end_date')
    device_types = get_device_types(service_type, begin_date, end_date)
    resp_str = json.dumps({"device_types": device_types})

    return HttpResponse(resp_str, content_type="text/json")


def get_version(request):
    service_type = request.GET.get('service_type')
    device_type = request.GET.get('device_type')
    begin_date = request.GET.get('begin_date')
    end_date = request.GET.get('end_date')
    versions = get_versions(service_type, device_type, begin_date, end_date)
    resp_str = json.dumps({"versions": versions})

    return HttpResponse(resp_str, content_type="text/json")

