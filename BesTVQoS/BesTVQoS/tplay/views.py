# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.db.models import Sum

from common.views import *
from common.date_time_tool import *

# from tplay.functions import process_single_qos, get_device_types, get_versions, process_multi_plot
from tplay.functions import *
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


def get_growth_percent(v1, v2):
    try:
        result = round(100.0 * (v1 - v2) / v2, 2)
    except ZeroDivisionError:
        result = None

    return result


def get_version_analyze_param(model, service_type, device_type, end_date):
    date_fmt = '%Y-%m-%d'
    end_date_tm = datetime.strptime(end_date, date_fmt)
    one_week_ago = (end_date_tm - timedelta(days=7)).strftime(date_fmt)
    filter_params = FilterParams(model, service_type, device_type, one_week_ago, end_date)
    days_region = get_days_region(one_week_ago, end_date)

    return filter_params, days_region


def play_records_analyze(service_type, device_type, end_date):
    header = ['类型', '数据', '环比上日(%)', '同比上周(%)', '一周均值', '一周峰值', '峰值日期']
    play_records = HtmlTable()
    play_records.mtitle = '播放量'
    play_records.mheader = header
    play_records.msub = []

    filter_params, days_region = get_version_analyze_param(BestvPlayinfo, service_type, device_type, end_date)

    data_by_day = prepare_daily_data_of_single_qos(filter_params, days_region, VIEW_TYPES,
                                                   'Records', True, 1, True)

    for view_type, desc in VIEW_TYPES:
        if any(data_by_day[view_type]) > 0:
            records_end_date = int(data_by_day[view_type][-1])
            day_on_day = get_growth_percent(records_end_date, data_by_day[view_type][-2])
            week_on_week = get_growth_percent(records_end_date, data_by_day[view_type][0])
            avg_week = int(sum(data_by_day[view_type][1:])/7)
            max_week, max_date = max(zip(data_by_day[view_type][1:], days_region[1:]), key=lambda x: x[0])
            play_records.msub.append([desc, records_end_date, day_on_day, week_on_week,
                                      avg_week, int(max_week), max_date])

    return play_records


def pn_values_analyze_summary(datum):
    """
    P25: play_time_end_date 294, day_on_day 0.0, week_on_week 2.08, avg 302, max 328, date 2015-06-04
    P50: play_time_end_date 1484, day_on_day 11.5, week_on_week 12.51, avg 1375, max 1484, date 2015-06-08
    P75: play_time_end_date 2615, day_on_day 0.54, week_on_week 0.65, avg 2607, max 2615, date 2015-06-08
    P90: play_time_end_date 4531, day_on_day -7.21, week_on_week 0.15, avg 4581, max 4953, date 2015-06-06
    P95: play_time_end_date 6862, day_on_day -1.68, week_on_week 7.76, avg 6696, max 7012, date 2015-06-06
    AVG: play_time_end_date 2241, day_on_day 1.91, week_on_week 7.69, avg 2174, max 2241, date 2015-06-08

    环比 p50:+11.5 p90:-7.21; 同比 p50:+12.51 p95:+7.76 AVG:+7.69; 其他各值变化幅度小于10%;
    具体数值(AVG/P50/P75/P90) 当日:2241/1484/2615/4531 一周均值:2174/1375/2607/4581 一周峰值:2241/1484/2615/4953
    """

    threshold = 10
    flags = ['↑', '↓']
    dod = '环比'
    wow = '同比'
    for pn in datum:
        data = datum[pn]
        dod_v = data[1]
        wow_v = data[2]
        if dod_v and abs(dod_v) >= threshold:
            dod += ' {0}{1}{2}'.format(pn, (flags[0] if dod_v > 0 else flags[1]), abs(dod_v))
        if wow_v and abs(wow_v) >= threshold:
            wow += ' {0}{1}{2}'.format(pn, (flags[0] if wow_v > 0 else flags[1]), abs(wow_v))

    # tip = '其他各值变化幅度小于10%'
    values = '具体数值(AVG/P50/P75/P90)'
    values += ' 当日:{0}/{1}/{2}/{3}'.format(datum['AVG'][0], datum['P50'][0], datum['P75'][0], datum['P90'][0])
    values += ' 一周均值:{0}/{1}/{2}/{3}'.format(datum['AVG'][3], datum['P50'][3], datum['P75'][3], datum['P90'][3])
    values += ' 一周峰值:{0}/{1}/{2}/{3}'.format(datum['AVG'][4], datum['P50'][4], datum['P75'][4], datum['P90'][4])

    # summary = '{0}; {1}; {2}; {3}'.format(dod, wow, tip, values)
    summary = '⑴{0}; ⑵{1}; ⑶{2}'.format(dod, wow, values)

    return summary

def play_time_analyze(service_type, device_type, end_date):
    play_time = HtmlTable()
    play_time.mtitle = '播放时长'
    play_time.mheader = ['类型', '概述']
    play_time.msub = []

    filter_params, days_region = get_version_analyze_param(BestvPlaytime, service_type, device_type, end_date)

    data_by_day = prepare_pnvalue_daily_data(filter_params, days_region, VIEW_TYPES[1:], PN_LIST, 1)

    for view_type, desc in VIEW_TYPES[1:]:
        datum = {}
        for pn, pn_desc in PN_LIST:
            if any(data_by_day[view_type][pn]) > 0:
                value = int(data_by_day[view_type][pn][-1])
                day_on_day = get_growth_percent(value, data_by_day[view_type][pn][-2])
                week_on_week = get_growth_percent(value, data_by_day[view_type][pn][0])
                avg_week = int(sum(data_by_day[view_type][pn][1:])/7)
                max_week, max_date = max(zip(data_by_day[view_type][pn][1:], days_region[1:]), key=lambda x: x[0])
                datum[pn_desc] = [value, day_on_day, week_on_week, avg_week, max_week, max_date]

        if datum:
            summary = pn_values_analyze_summary(datum)
            play_time.msub.append([desc, summary])

    return play_time


def user_activity_analyze(service_type, device_type, end_date):
    # 版本活跃度
    user_activity = HtmlTable()
    header = ['类型', '数据', '环比上日(%)', '同比上周(%)', '一周均值', '一周峰值', '峰值日期']
    user_activity.mtitle = '用户活跃度'
    user_activity.mheader = header
    user_activity.msub = []

    filter_params, days_region = get_version_analyze_param(BestvPlayprofile, service_type, device_type, end_date)

    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')

    results = filter_params.table.objects.filter(q_conditions)

    process_items = [(0, '用户数'), (1, '人均播放时长'), (2, '人均播放次数'), (3, '单次观看时长')]
    data_date = {}
    for row in results:
        d = str(row.Date)
        data_date[(d, 0)] = row.Users
        data_date[(d, 1)] = row.AverageTime
        data_date[(d, 2)] = row.Records / row.Users
        data_date[(d, 3)] = row.AverageTime * row.Users / row.Records

    data_by_day = {}
    for i, desc in process_items:
        data_by_day[i] = []
        for d in days_region:
            data_by_day[i].append(data_date.get((d, i), 0))

    for i, desc in process_items:
        if any(data_by_day[i]) > 0:
            value = int(data_by_day[i][-1])
            day_on_day = get_growth_percent(value, data_by_day[i][-2])
            week_on_week = get_growth_percent(value, data_by_day[i][0])
            avg_week = int(sum(data_by_day[i][1:])/7)
            max_week, max_date = max(zip(data_by_day[i][1:], days_region[1:]), key=lambda x: x[0])
            user_activity.msub.append([desc, value, day_on_day, week_on_week,
                                      avg_week, int(max_week), max_date])

    return user_activity


def qos_fbuffer_analyze(service_type, device_type, end_date):
    # 服务质量
    view_types = VIEW_TYPES[1:]
    process_items = [(0, '缓冲成功率'), (1, '一次不卡比例'), (2, '卡用户卡时长占比'), (3, '卡播放平均卡次数')]

    filter_params, days_region = get_version_analyze_param(None, service_type, device_type, end_date)
    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')

    # data_date[(date, type 0/1, view_type, index)]
    # @type 0: for qos
    # @type 1: for fbuffer
    data_date = {}

    results = BestvFbuffer.objects.filter(q_conditions)
    for row in results:
        d = str(row.Date)
        data_date[(d, 0, row.ViewType, 0)] = 100*row.SucRatio
        for (pn, _) in PN_LIST:
            data_date[(d, 1, row.ViewType, pn)] = getattr(row, pn)

    results1 = BestvFluency.objects.filter(q_conditions)
    for row in results1:
        d = str(row.Date)
        data_date[(d, 0, row.ViewType, 1)] = 100*row.Fluency
        data_date[(d, 0, row.ViewType, 2)] = 100*row.PRatio
        data_date[(d, 0, row.ViewType, 3)] = row.AvgCount

    # qos
    qos_by_day = {}
    for v, v_desc in view_types:
        for i, i_desc in process_items:
            qos_by_day[(v, i)] = []
            for d in days_region:
                qos_by_day[(v, i)].append(data_date.get((d, 0, v, i), 0.0))

    header = ['类型', '数据', '环比上日(%)', '同比上周(%)', '一周均值', '一周峰值', '峰值日期']
    qos = list()
    for v, v_desc in view_types:
        qos.append(HtmlTable())
        qos[-1].mtitle = '{0}服务质量'.format(v_desc)
        qos[-1].mheader = header
        qos[-1].msub = []
        has_data = False
        for i, i_desc in process_items:
            if any(qos_by_day[(v, i)]) > 0:
                has_data = True
                value = qos_by_day[(v, i)][-1]
                day_on_day = get_growth_percent(value, qos_by_day[(v, i)][-2])
                week_on_week = get_growth_percent(value, qos_by_day[(v, i)][0])
                avg_week = int(sum(qos_by_day[(v, i)][1:])/7)
                max_week, max_date = max(zip(qos_by_day[(v, i)][1:], days_region[1:]), key=lambda x: x[0])
                qos[-1].msub.append([i_desc, value, day_on_day, week_on_week, avg_week, int(max_week), max_date])
        if not has_data:
            qos.pop()

    # fbuffer
    fbuffer = HtmlTable()
    fbuffer.mtitle = '首次缓冲时长'
    fbuffer.mheader = ['类型', '概述']
    fbuffer.msub = []

    fbuffer_by_day = {}
    for v, v_desc in view_types:
        pn_values = {}
        for (pn, _) in PN_LIST:
            pn_values[pn] = []
            for d in days_region:
                pn_values[pn].append(data_date.get((d, 1, v, pn), 0))

        fbuffer_by_day[v] = pn_values

    for v, v_desc in view_types:
        datum = {}
        for pn, pn_desc in PN_LIST:
            if any(fbuffer_by_day[v][pn]) > 0:
                value = int(fbuffer_by_day[v][pn][-1])
                day_on_day = get_growth_percent(value, fbuffer_by_day[v][pn][-2])
                week_on_week = get_growth_percent(value, fbuffer_by_day[v][pn][0])
                avg_week = int(sum(fbuffer_by_day[v][pn][1:])/7)
                max_week, max_date = max(zip(fbuffer_by_day[v][pn][1:], days_region[1:]), key=lambda x: x[0])
                datum[pn_desc] = [value, day_on_day, week_on_week, avg_week, max_week, max_date]

        if datum:
            summary = pn_values_analyze_summary(datum)
            fbuffer.msub.append([v_desc, summary])

    return qos, fbuffer


@login_required
def show_version_analyze(request):
    context = dict()

    (service_type, device_type, device_types,
     version, versions, begin_date, end_date) = get_filter_param_values(request)

    if device_type == "":
        raise NoDataError("No data on {0} in tplay_title".format(end_date))

    if version == "All":
        device_type_full = device_type
    else:
        device_type_full = '{0}_{1}'.format(device_type, version)

    # 播放量与播放时长
    context['items'] = ['播放量与播放时长']
    context['play_records'] = play_records_analyze(service_type, device_type_full, end_date)
    context['play_time'] = play_time_analyze(service_type, device_type_full, end_date)

    # 版本活跃度
    context['items'].append('版本活跃度')
    context['user_activity'] = user_activity_analyze(service_type, device_type_full, end_date)

    # 服务质量
    context['items'].append('服务质量')
    qos, fbuffer = qos_fbuffer_analyze(service_type, device_type_full, end_date)
    context['qos'] = qos
    context['fbuffer'] = fbuffer

    context['service_types'] = SERVICE_TYPES
    context['default_service_type'] = service_type
    context['device_types'] = device_types
    context['default_device_type'] = device_type
    context['versions'] = versions
    context['default_version'] = version
    context['default_end_date'] = end_date

    response = render_to_response('show_version_analyze.html', context)
    # set_default_values_to_cookie(response, context)

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

