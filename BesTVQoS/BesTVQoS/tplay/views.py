# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.db.models import Sum, Q
from common.views import *
from common.date_time_tool import *
from tplay.functions import process_single_qos, get_device_types, get_versions, process_multi_plot
from tplay.models import *

logger = logging.getLogger("django.request")

SERVICE_TYPES = ["All", "B2B", "B2C"]
VIEW_TYPES = [(0, "总体"), (1, "点播"), (2, "回看"), (3, "直播"), (4, "连看"), (5, "未知")]
PN_LIST = [("P25", "P25"), ("P50", "P50"), ("P75", "P75"),
           ("P90", "P90"), ("P95", "P95"), ("AverageTime", "AVG")]

def get_playing_stat_today(service_type, date_str, min_rec):
    table = HtmlTable()
    table.mtitle = "今日用户播放统计信息（每小时更新）"
    table.mheader = ["服务类型", "设备类型", "播放数", '播放百分比%']
    table.msub = []
    subs = []

    q_conditions = Q(Date=date_str) & Q(DeviceType__contains='.')
    if service_type != 'All':
        q_conditions = q_conditions & Q(ServiceType=service_type)
        if service_type == 'B2C':
            q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')

    records_total = BestvPlayinfo.objects.filter(q_conditions).aggregate(Sum('Records')).get('Records__sum')

    if records_total:
        q_conditions = q_conditions & Q(Records__gte=min_rec)
        results = BestvPlayinfo.objects.filter(q_conditions)\
            .values('ServiceType', 'DeviceType')\
            .annotate(Sum('Records')).order_by('-Records__sum')

        for row in results:
            sub = list()
            sub.append(row['ServiceType'])
            sub.append(row['DeviceType'])
            sub.append(row['Records__sum'])
            sub.append(round(100.0 * float(row['Records__sum']) / records_total, 2))
            subs.append(sub)
            table.msub.append(sub)
    else:
        logger.error("Unexpected Value: records_total: {0}".format(records_total))

    return table


def get_playing_stat_history(service_type, date_str, min_rec):
    table = HtmlTable()
    table.mtitle = "{0} 用户播放统计信息".format(date_str)
    table.mheader = ['服务类型', '设备类型', '播放数', '播放百分比%',
                     '用户数', '用户百分比%', '人均播放时间', '人均播放次数']
    table.msub = []
    subs = []

    q_conditions = Q(Date=date_str) & Q(DeviceType__contains='.')
    if service_type != 'All':
        q_conditions = q_conditions & Q(ServiceType=service_type)
        if service_type == 'B2C':
            q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')

    totals = BestvPlayprofile.objects.filter(q_conditions).aggregate(Sum('Records'), Sum('Users'))
    records_total = totals.get('Records__sum')
    users_total = totals.get('Users__sum')

    if records_total and users_total:
        q_conditions = q_conditions & Q(Records__gte=min_rec)
        results = BestvPlayprofile.objects.filter(q_conditions)\
            .values('ServiceType', 'DeviceType', 'Records', 'Users', 'AverageTime')\
            .order_by('-Records')

        for row in results:
            sub = list()
            sub.append(row['ServiceType'])
            sub.append(row['DeviceType'])
            sub.append(row['Records'])
            sub.append(round(100.0 * float(row['Records']) / records_total, 2))
            sub.append(row['Users'])
            sub.append(round(100.0 * float(row['Users']) / users_total, 2))
            sub.append(row['AverageTime'])
            if row['Users'] > 0:
                sub.append(row['Records'] / row['Users'])
            else:
                sub.append(0)
            subs.append(sub)
            table.msub.append(sub)
    else:
        logger.error("Unexpected Value: records_total: {0}, users_total: {1}".format(records_total, users_total))

    return table


@login_required
def show_playing_stat(request):
    begin_time = current_time()
    service_type = request.GET.get('service_type', 'All')
    date_str = request.GET.get('date', todaystr())
    min_rec = request.GET.get('min_rec', 0)

    if date_str == todaystr():
        table = get_playing_stat_today(service_type, date_str, min_rec)
    else:
        table = get_playing_stat_history(service_type, date_str, min_rec)

    context = dict()
    context['table'] = table
    context['default_date'] = date_str
    context['default_min_rec'] = min_rec
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES

    cost_time = current_time() - begin_time
    logger.debug('show_playing_stat {0} cost {1}s'.format(date_str, cost_time))

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
    # begin_date = request.GET.get('begin_date')
    # end_date = request.GET.get('end_date')
    device_types = get_device_types(service_type)
    resp_str = json.dumps({"device_types": device_types})

    return HttpResponse(resp_str, content_type="text/json")


def get_version(request):
    service_type = request.GET.get('service_type')
    device_type = request.GET.get('device_type')
    # begin_date = request.GET.get('begin_date')
    # end_date = request.GET.get('end_date')
    versions = get_versions(service_type, device_type)
    resp_str = json.dumps({"versions": versions})

    return HttpResponse(resp_str, content_type="text/json")

