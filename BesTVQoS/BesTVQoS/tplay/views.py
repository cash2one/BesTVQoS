# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.db.models import Sum

from common.views import *
from common.date_time_tool import *

from loganalyze.server_views import get_multidays_interval

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


@time_func
def get_version_analyze_param(model, service_type, device_type, end_date):
    date_fmt = '%Y-%m-%d'
    end_date_tm = datetime.strptime(end_date, date_fmt)
    one_week_ago = (end_date_tm - timedelta(days=7)).strftime(date_fmt)
    filter_params = FilterParams(model, service_type, device_type, one_week_ago, end_date)
    days_region = get_days_region(one_week_ago, end_date)

    return filter_params, days_region


@time_func
def play_records_analyze(service_type, device_type, end_date):
    filter_params, days_region = get_version_analyze_param(BestvPlayinfo, service_type, device_type, end_date)
    data_by_day = prepare_daily_data_of_single_qos(filter_params, days_region, VIEW_TYPES,
                                                   'Records', True, 1, True)

    series = list()
    for view_type, desc in VIEW_TYPES[1:]:
        if any(data_by_day[view_type]):
            series.append({'name': desc, 'data': [int(v) for v in data_by_day[view_type]]})

    distribution = dict()
    distribution['title'] = '各观看类型占比'
    distribution['subtitle'] = ''
    distribution['x'] = days_region
    distribution['series'] = series

    return distribution


@time_func
def qos_fbuffer_analyze(service_type, device_type, begin_date, end_date, index=0):
    view_types = VIEW_TYPES[1:]
    x_alis_day = get_days_region(begin_date, end_date)
    x_alis = []
    for d in x_alis_day:
        x_alis_hour = ["%s:00" % i for i in range(24)]
        x_alis_hour[0] = d
        x_alis += x_alis_hour

    data_count = len(x_alis)

    q_conditions = Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    q_conditions = q_conditions & Q(DeviceType=device_type)
    q_conditions = q_conditions & Q(ServiceType=service_type)
    if service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions &= Q(Hour__lt=24)

    # initial fbuffer: P50, P90, AverageTime
    pn_list = [('P50', 'P50'), ('P90', 'P90'), ('AverageTime', 'AVG')]
    datas_fbuffer = {}
    for view, desc in view_types:
        datas_fbuffer[view] = {}
        for i, _ in pn_list:
            datas_fbuffer[view][i] = [0 for _ in range(data_count)]

    # initial qos: '缓冲成功率', '一次不卡比例', '卡用户卡时长占比'
    qos_items = [('suc_ratio', '缓冲成功率'), ('fluency', '一次不卡比例'), ('p_ratio', '卡用户卡时长占比')]
    datas_qos = {}
    for view, desc in view_types:
        datas_qos[view] = {}
        for i, _ in qos_items:
            datas_qos[view][i] = [0 for _ in range(data_count)]

    # fbuffer
    q_extra = Q(AverageTime__gt=0) | Q(P90__gt=0) | Q(P50__gt=0)
    results = BestvFbuffer.objects.filter(q_conditions).filter(q_extra)\
        .values('ViewType', 'Date', 'Hour', 'SucRatio', 'P50', 'P90', 'AverageTime')
    for row in results:
        i = get_days_offset(begin_date, str(row['Date'])) * 24 + row['Hour']
        datas_qos[row['ViewType']]['suc_ratio'][i] = 100*row['SucRatio']
        datas_fbuffer[row['ViewType']]['P50'][i] = row['P50']
        datas_fbuffer[row['ViewType']]['P90'][i] = row['P90']
        datas_fbuffer[row['ViewType']]['AverageTime'][i] = row['AverageTime']

    # qos
    q_extra = Q(Fluency__gt=0) | Q(PRatio__gt=0)
    results1 = BestvFluency.objects.filter(q_conditions).filter(q_extra)\
        .values('ViewType', 'Date', 'Hour', 'Fluency', 'PRatio')
    for row in results1:
        i = get_days_offset(begin_date, str(row['Date'])) * 24 + row['Hour']
        datas_qos[row['ViewType']]['fluency'][i] = 100*row['Fluency']
        datas_qos[row['ViewType']]['p_ratio'][i] = 100*row['PRatio']

    items_qos_fb = []
    interval = get_multidays_interval(len(x_alis)/24)
    for (v, desc) in view_types:
        item = make_plot_item(datas_qos[v], qos_items, index, x_alis, '{0} QoS'.format(desc),
                              '', '百分比(%)', interval)
        if item:
            items_qos_fb.append(item)
            index += 1

        item = make_plot_item(datas_fbuffer[v], pn_list, index, x_alis, '{0} fbuffer'.format(desc),
                              '', '秒(s)', interval)
        if item:
            items_qos_fb.append(item)
            index += 1

    return items_qos_fb


def prepare_hourly_play_records(service_type, device_type, begin_date, end_date, x_alis, view_types):
    data_count = len(x_alis)

    q_condition = Q(ServiceType=service_type) & Q(DeviceType=device_type)
    if service_type == 'B2C':
        q_condition &= Q(ISP='all') & Q(Area='all')
    q_condition &= Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    q_condition &= Q(Hour__lt=24) & Q(Records__gt=0)

    results = BestvPlayinfo.objects.filter(q_condition).values('Date', 'Hour', 'ViewType', 'Records')

    datas = {}
    for view, desc in view_types:
        datas[view] = [0 for _ in range(data_count)]

    for row in results:
        index = get_days_offset(begin_date, str(row['Date'])) * 24 + row['Hour']
        datas[row['ViewType']][index] = row['Records']

    datas[0] = map(sum, zip(*datas.values()))

    return datas


def get_play_records(service_type, device_type, begin_date, end_date, index=0):
    view_types = VIEW_TYPES

    x_alis_day = get_days_region(begin_date, end_date)
    x_alis = []
    for d in x_alis_day:
        x_alis_hour = ["%s:00" % i for i in range(24)]
        x_alis_hour[0] = d
        x_alis += x_alis_hour

    datas = prepare_hourly_play_records(service_type, device_type, begin_date, end_date, x_alis, view_types)
    interval = get_multidays_interval(len(x_alis)/24)
    item = make_plot_item(datas, view_types, index, x_alis, '各类型观看量(已隐藏无观看量的类型)',
                          '', '记录数', interval, remove_zero_serie=True)

    return item


def prepare_daily_users(service_type, device_type, begin_date, end_date, x_alis, keys):
    data_count = len(x_alis)

    q_condition = Q(ServiceType=service_type) & Q(DeviceType=device_type)
    if service_type == 'B2C':
        q_condition &= Q(ISP='all') & Q(Area='all')
    q_condition &= Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    q_condition &= Q(Records__gt=0) & Q(Users__gt=0)

    results = BestvPlayprofile.objects.filter(q_condition).values('Date', 'Records', 'Users')

    datas = {}
    for k, desc in keys:
        datas[k] = [0 for _ in range(data_count)]

    for row in results:
        index = get_days_offset(begin_date, str(row['Date']))
        datas['Records'][index] = row['Records']
        datas['Users'][index] = row['Users']

    return datas


def get_users(service_type, device_type, begin_date, end_date, index=0):
    keys = [('Records', "记录数"), ('Users', "用户数")]

    x_alis = get_days_region(begin_date, end_date)
    datas = prepare_daily_users(service_type, device_type, begin_date, end_date, x_alis, keys)
    item = make_plot_item(datas, keys, index, x_alis, '总观看量及用户数',
                          '', 'Num', remove_zero_serie=True)

    return item


@login_required
def show_version_analyze(request):
    context = dict()

    (service_type, device_type, device_types,
     version, versions, begin_date, end_date) = get_filter_param_values(request)

    date_fmt = '%Y-%m-%d'
    end_date_tm = datetime.strptime(end_date, date_fmt)
    one_week_ago = (end_date_tm - timedelta(days=7)).strftime(date_fmt)

    if version == "All":
        device_type_full = device_type
    else:
        device_type_full = '{0}_{1}'.format(device_type, version)

    # 播放量与播放时长
    context['items'] = ['播放量与用户数']
    items = []
    play_records = get_play_records(service_type, device_type_full, one_week_ago, end_date, len(items))
    items.append(play_records)

    users = get_users(service_type, device_type_full, one_week_ago, end_date, len(items))
    items.append(users)

    context['distribution'] = play_records_analyze(service_type, device_type_full, end_date)

    # 服务质量
    context['items'].append('服务质量')
    items_qos_fb = qos_fbuffer_analyze(service_type, device_type_full, one_week_ago, end_date, len(items))
    items.extend(items_qos_fb)
    context['items_qos_fb_index'] = [i+2 for i in range(len(items_qos_fb))]

    context['contents'] = items
    context['service_types'] = SERVICE_TYPES
    context['default_service_type'] = service_type
    context['device_types'] = device_types
    context['default_device_type'] = device_type
    context['versions'] = versions
    context['default_version'] = version
    context['default_begin_date'] = begin_date if begin_date <= end_date else end_date
    context['default_end_date'] = end_date

    response = render_to_response('show_version_analyze.html', context)
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

def get_one_day_users(request, date_str):
    results = BestvPlayprofile.objects.filter(Date=date_str).values('ServiceType', 'DeviceType', 'Users')

    users_list = [row for row in results]

    # noinspection PyBroadException
    try:
        resp = json.dumps(users_list)
    except:
        resp = list()

    return HttpResponse(resp, content_type="text/json")