# -*- coding: utf-8 -*-
import logging
import time

from django.db.models import Q
from common.date_time_tool import current_time, get_days_region
from common.views import get_default_values_from_cookie
from tplay.models import Title

logger = logging.getLogger("django.request")
SERVICE_TYPES = ["B2B", "B2C"]
HOUR_X_AXIS = range(24)

def trace_func(func):
    def wrapper(*args, **kwargs):
        logger.debug("before call {0}({1},{2})".format(func.__name__, args, kwargs))
        result = func(*args, **kwargs)
        logger.debug("after call {0}({1},{2}) \nreturn={3}".format(func.__name__,args, kwargs, result))
        return result
    return wrapper


def time_func(func):
    def wrapper(*args, **kwargs):
        begin_time = current_time()
        result = func(*args, **kwargs)
        cost_time = current_time() - begin_time
        logger.debug("{0}({1},{2}) cost {3}s".format(func.__name__, args, kwargs, cost_time))
        return result

    return wrapper


class NoDataError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FilterParams:
    def __init__(self, table, service_type, device_type, begin_date, end_date):
        self.table = table
        self.service_type = service_type
        self.device_type = device_type
        self.begin_date = begin_date
        self.end_date = end_date


# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, x_axis, title, subtitle, y_title):
    item = dict()
    item["index"] = item_idx
    item["title"] = title
    item["subtitle"] = subtitle
    item["y_title"] = y_title
    item["xAxis"] = x_axis
    item["t_interval"] = 1
    if len(x_axis) > 30:
        item["t_interval"] = len(x_axis) / 30

    series = []
    for (i, desc) in keys:
        serie_item = '''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }''' % (desc, ",".join(['{0}'.format(v) for v in key_values[i]]))
        series.append(serie_item)

    item["series"] = ",".join(series)

    return item

# @trace_func
def prepare_daily_data_of_single_qos(filter_params, days_region, view_types, qos_name, hour_flag, base_radix, need_total=False):
    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    if hour_flag:
        q_conditions = q_conditions & Q(Hour=24)

    results = filter_params.table.objects.filter(q_conditions)

    view_type_date = {}
    for row in results:
        view_type_date[(str(row.Date), getattr(row, 'ViewType', 0))] = getattr(row, qos_name)

    data_by_day = {}
    for view_type in [view_type[0] for view_type in view_types]:
        data_by_day[view_type] = []
        for day in days_region:
            data_by_day[view_type].append(view_type_date.get((day, view_type), 0.0) * base_radix)

    if need_total:
        data_by_day[0] = map(sum, zip(*data_by_day.values()))

    return data_by_day

# @trace_func
def prepare_hour_data_of_single_qos(filter_params, view_types, qos_name, base_radix, need_total=False):
    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions = q_conditions & Q(Hour__lt=24)

    results = filter_params.table.objects.filter(q_conditions)

    view_type_hour = {}
    for row in results:
        view_type_hour[(row.Hour, getattr(row, 'ViewType', 0))] = getattr(row, qos_name)

    data_by_hour = {}
    for view_type in [view_type[0] for view_type in view_types]:
        data_by_hour[view_type] = []
        for hour in range(24):
            data_by_hour[view_type].append(view_type_hour.get((hour, view_type), 0.0) * base_radix)

    if need_total:
        data_by_hour[0] = map(sum, zip(*data_by_hour.values()))

    # logger.debug("data_by_hour: {0}".format(data_by_hour))

    return data_by_hour

# @trace_func
@time_func
def get_device_types(service_type):
    q_conditions = Q(ServiceType=service_type)
    titles = Title.objects.filter(q_conditions).values('DeviceType').distinct()
    device_types = []
    type_set = set()
    for title in titles:
        type_set.add(title['DeviceType'])

    device_types.extend(sorted(type_set, key=unicode.lower))

    return device_types

# @trace_func
@time_func
def get_versions(service_type, device_type):
    q_conditions = Q(ServiceType=service_type) & Q(DeviceType=device_type)

    titles = Title.objects.filter(q_conditions).values('Version')

    versions = set()
    for title in titles:
        versions.add(title['Version'])

    version_list = ['All']
    version_list.extend(sorted(versions))

    return version_list


def get_filter_param_values(request):
    filters_map = get_default_values_from_cookie(request)
    service_type = request.GET.get("service_type", filters_map["st"]).encode("utf-8")
    device_type = request.GET.get("device_type", filters_map["dt"]).encode("utf-8")
    version = request.GET.get("version", filters_map["vt"]).encode("utf-8")
    begin_date = request.GET.get("begin_date", filters_map["begin"]).encode("utf-8")
    end_date = request.GET.get("end_date", filters_map["end"]).encode("utf-8")
    # logger.info("get_filter_values: %s - %s - %s" % (service_type, device_type, version))

    device_types = get_device_types(service_type)
    if len(device_types) == 0:
        device_types = [""]
        device_type = ""

    if device_type not in device_types:
        device_type = device_types[0]

    versions = []
    try:
        versions = get_versions(service_type, device_type)
    except:
        logger.info("get_versions({0}, {1}, {2}, {3}) failed.".format(
            service_type, device_type, begin_date, end_date))

    if len(versions) == 0:
        versions = [""]
        version = ""
    if version not in versions:
        version = versions[0]
    
    return service_type, device_type, device_types, version, versions, begin_date, end_date


def process_single_qos(request, table, qos_name, title, subtitle, y_title, view_types, hour_flag, base_radix=1):
    begin_time = time.time()
    items = []

    try:
        (service_type, device_type, device_types,
            version, versions, begin_date, end_date) = get_filter_param_values(request)

        if device_type == "":
            raise NoDataError("No data between {0} and {1} in tplay_title".format(begin_date, end_date))

        if version == "All":
            device_type_full = device_type
        else:
            device_type_full = '{0}_{1}'.format(device_type, version)

        filter_params = FilterParams(table, service_type, device_type_full, begin_date, end_date)

        # ViewType (0, '总体') indicates total, if so, it should be the first item of view_types
        if 0 in view_types[0] and len(view_types) > 1:
            need_total = True
        else:
            need_total = False

        if begin_date == end_date and hour_flag:
            data_by_hour = prepare_hour_data_of_single_qos(
                filter_params, view_types, qos_name, base_radix, need_total)

            if data_by_hour is None:
                raise NoDataError("No hour data between {0} and {1}".format(begin_date, end_date))

            item = make_plot_item(data_by_hour, view_types, 0, HOUR_X_AXIS, title, subtitle, y_title)
            items.append(item)
        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_daily_data_of_single_qos(
                filter_params, days_region, view_types, qos_name, hour_flag, base_radix, need_total)
            if data_by_day is None:
                raise NoDataError("No daily data between {0} and {1}".format(begin_date, end_date))

            format_days_region = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
            item = make_plot_item(data_by_day, view_types, 0, format_days_region, title, subtitle, y_title)
            items.append(item)

    except Exception, e:
        logger.info("query {0} {1} error: {2}".format(table.__name__, qos_name, e))
        # raise

    context = dict()
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents'] = items
    if len(items) > 0:
        context['has_data'] = True

    logger.info("query {0} {1} cost {2}".format(table.__name__, qos_name, (time.time() - begin_time)))

    return context


# For multi Qos, such as pnvalue, display: multi plots of single view type
# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}

# @trace_func
def prepare_pnvalue_hour_data(filter_params, view_types, pn_types, base_radix):
    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions = q_conditions & Q(Hour__lt=24)

    results = filter_params.table.objects.filter(q_conditions)

    view_type_hour = {}
    for row in results:
        for (pn, _) in pn_types:
            view_type_hour[(pn, row.Hour, row.ViewType)] = getattr(row, pn) / base_radix

    data_by_hour = {}
    for view_type in [view_type[0] for view_type in view_types]:
        display_data = {}
        for (pn, _) in pn_types:
            display_data[pn] = []
            for hour in range(24):
                display_data[pn].append(view_type_hour.get((pn, hour, view_type), 0.0))

        data_by_hour[view_type] = display_data

    # logger.debug("data_by_hour: {0}".format(data_by_hour))

    return data_by_hour

# output: key-values: key: viewType, values:{"P25":[xxx], "P50":[xxx], ...}

# @trace_func
def prepare_pnvalue_daily_data(filter_params, days_region, view_types, pn_types, base_radix):
    q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(ServiceType=filter_params.service_type)
    if filter_params.service_type == 'B2C':
        q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions = q_conditions & Q(Hour=24)

    results = filter_params.table.objects.filter(q_conditions)

    view_type_date = {}
    for row in results:
        for (pn, _) in pn_types:
            view_type_date[(pn, str(row.Date), row.ViewType)] = getattr(row, pn) / base_radix

    data_by_date = {}
    for view_type in [view_type[0] for view_type in view_types]:
        display_data = {}
        for (pn, _) in pn_types:
            display_data[pn] = []
            for day in days_region:
                display_data[pn].append(view_type_date.get((pn, day, view_type), 0.0))

        data_by_date[view_type] = display_data

    # logger.debug("data_by_date: {0}".format(data_by_date))

    return data_by_date


def process_multi_plot(request, table, title, subtitle, y_title, view_types, pn_types, base_radix=1):
    begin_time = current_time()
    items = []

    try:
        (service_type, device_type, device_types,
            version, versions, begin_date, end_date) = get_filter_param_values(request)
        if device_type == "":
            raise NoDataError("No data between {0} and {1} in tplay_title".format(begin_date, end_date))

        if version == "All":
            device_type_full = device_type
        else:
            device_type_full = '{0}_{1}'.format(device_type, version)

        filter_params = FilterParams(table, service_type, device_type_full, begin_date, end_date)

        if begin_date == end_date:
            data_by_hour = prepare_pnvalue_hour_data(filter_params, view_types, pn_types, base_radix)

            if data_by_hour is None:
                raise NoDataError("No hour data between {0} and {1}".format(begin_date, end_date))

            item_idx = 0
            for (view_type_idx, view_des) in view_types:
                if view_type_idx not in data_by_hour:
                    continue

                item = make_plot_item(data_by_hour[view_type_idx], pn_types, item_idx, HOUR_X_AXIS,
                                      title, "%s %s" % (subtitle, view_des), y_title)
                items.append(item)
                item_idx += 1
        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_pnvalue_daily_data(filter_params, days_region, view_types,
                                                     pn_types, base_radix)
            if data_by_day is None:
                raise NoDataError("No daily data between %s - %s" % (begin_date, end_date))

            format_days_region = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
            item_idx = 0
            for (view_type_idx, view_des) in view_types:
                if view_type_idx not in data_by_day:
                    continue
                item = make_plot_item(data_by_day[view_type_idx], pn_types, item_idx, format_days_region, title,
                                      "%s %s" % (subtitle, view_des), y_title)
                items.append(item)
                item_idx += 1

    except Exception, e:
        logger.info("query %s multiQos error: %s" % (table.__name__, e))

    context = dict()
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['contents'] = items
    if len(items) > 0:
        context['has_data'] = True

    logger.info("query %s multiQos, cost: %s" %
                (table.__name__, (current_time() - begin_time)))

    return context
