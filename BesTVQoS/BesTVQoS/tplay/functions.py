# -*- coding: utf-8 -*-
from django.db.models import Q
import logging
import time

from common.date_time_tool import current_time, today, get_days_region
from common.views import get_default_values_from_cookie
from tplay.fbuffer_views import NoDataError
from tplay.models import BestvFbuffer, Title

logger = logging.getLogger("django.request")
SERVICE_TYPES = ["B2B", "B2C"]
HOUR_XAXIS = range(24)

def tracefunc(func):
    def wrapper(*args,**kwargs):
        print "before call {0}({1},{2})".format(func.__name__,args, kwargs)
        result = func(*args, **kwargs)
        print "after call {0}({1},{2}) \nreturn={3}".format(func.__name__,args, kwargs, result)
        return result
    return wrapper

class FilterParams:
    def __init__(self, table, servicetype, devicetype, begin_date, end_date):
        self.table = table
        self.servicetype = servicetype
        self.devicetype = devicetype
        self.begin_date = begin_date
        self.end_date = end_date

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_plot_item(key_values, keys, item_idx, xaxis, title, subtitle, ytitle):
    item = {}
    item["index"] = item_idx
    item["title"] = title  # "首次缓冲成功率"
    item["subtitle"] = subtitle  # "全天24小时/全类型"
    item["y_title"] = ytitle  # "成功率"
    item["xAxis"] = xaxis
    item["t_interval"] = 1
    if len(xaxis) > 30:
        item["t_interval"] = len(xaxis) / 30
    series = []
    for (i, desc) in keys:
        serie_item = '''{
            name: '%s',
            yAxis: 0,
            type: 'spline',
            data: [%s]
        }''' % (desc, ",".join(key_values[i]))
        series.append(serie_item)
    item["series"] = ",".join(series)
    return item

@tracefunc
def prepare_daily_data_of_single_Qos(filter_params, days_region, view_types, Qos_name, hour_flag, base_radix):

    Q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    Q_conditions = Q_conditions & Q(DeviceType=filter_params.devicetype)
    if filter_params.servicetype != "All":
        Q_conditions = Q_conditions & Q(ServiceType=filter_params.servicetype)
    Q_conditions = Q_conditions & Q(ViewType__in=[view_type[0] for view_type in view_types])
    if hour_flag:
        Q_conditions = Q_conditions & Q(Hour=24)

    fbuffers = BestvFbuffer.objects.filter(Q_conditions)
    view_type_date = {}
    for fbuffer in fbuffers:
        view_type_date[(str(fbuffer.Date),fbuffer.ViewType)] = getattr(fbuffer,Qos_name)

    data_by_day = {}
    for view_type in [view_type[0] for view_type in view_types]:
        data_by_day[view_type] = []
        for date in days_region:
            data_by_day[view_type].append('%.1f' % (view_type_date.get((date,view_type), 0.0) * base_radix))

    return data_by_day
@tracefunc
def prepare_hour_data_of_single_Qos(filter_params, view_types, qos_name, base_radix):

    Q_conditions = Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    Q_conditions = Q_conditions & Q(DeviceType=filter_params.devicetype)
    if filter_params.servicetype != "All":
        Q_conditions = Q_conditions & Q(ServiceType=filter_params.servicetype)
    Q_conditions = Q_conditions & Q(ViewType__in=[view_type[0] for view_type in view_types])
    Q_conditions = Q_conditions & Q(Hour__lt=24)

    fbuffers = BestvFbuffer.objects.filter(Q_conditions)

    view_type_hour = {}
    for fbuffer in fbuffers:
        view_type_hour[(str(fbuffer.Hour),fbuffer.ViewType)] = getattr(fbuffer,qos_name)

    data_by_hour = {}
    for view_type in [view_type[0] for view_type in view_types]:
        data_by_hour[view_type] = []
        for hour in range(24):
            data_by_hour[view_type].append('%.1f' % (view_type_hour.get((str(hour),view_type), 0.0) * base_radix))

    return data_by_hour
@tracefunc
def get_device_types(service_type, begin_date, end_date):
    Q_conditions = Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    Q_conditions = Q_conditions & Q(ServiceType=service_type)
    Q_conditions = Q_conditions & ~Q(DeviceType__contains=".")
    titles = Title.objects.filter(Q_conditions)
    device_types = []
    type_set = set()
    for title in titles:
        type_set.add(title.DeviceType)
    device_types.extend(sorted(type_set))
    return device_types
@tracefunc
def get_versions(service_type, device_type, begin_date, end_date):
    Q_conditions = Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    Q_conditions = Q_conditions & Q(ServiceType=service_type)
    Q_conditions = Q_conditions & Q(DeviceType__startswith="{0}_".format(device_type))

    titles = Title.objects.filter(Q_conditions)
    print(len(titles))
    version_pos = len(device_type) + 1
    #device_types = ["All"]
    versions = set()
    for title in titles:
        version = title.DeviceType[version_pos:]
        versions.add(version)

    return sorted(versions)

def get_filter_param_values(request, table):
    begin_time = current_time()
    filters_map = get_default_values_from_cookie(request)
    service_type = request.GET.get("service_type", filters_map["st"]).encode("utf-8")
    device_type = request.GET.get("device_type", filters_map["dt"]).encode("utf-8")
    version = request.GET.get("version", filters_map["vt"]).encode("utf-8")
    begin_date = request.GET.get("begin_date", filters_map["begin"]).encode("utf-8")
    end_date = request.GET.get("end_date", filters_map["end"]).encode("utf-8")
    logger.info("get_filter_values: %s - %s - %s" %
                (service_type, device_type, version))

    device_types = get_device_types(service_type, begin_date, end_date)
    if len(device_types) == 0:
        device_types = [""]
        device_type = ""

    if device_type not in device_types:
        device_type = device_types[0]
    logger.info("get_filter_param_values1 %s %s, cost: %s" %
                (device_type, version, (current_time() - begin_time)))

    versions = []
    try:
        versions = get_versions(service_type, device_type, begin_date, end_date)
    except Exception, e:
        logger.info("get_versions(%s, %s, %s, %s, %s) failed." % (
            table, service_type, device_type, begin_date, end_date))

    if len(versions) == 0:
        versions = [""]
        version = ""
    if version not in versions:
        version = versions[0]

    logger.info("get_filter_param_values %s %s, cost: %s" %
                (device_type, version, (current_time() - begin_time)))
    return service_type, device_type, device_types, version, versions, begin_date, end_date

def process_single_Qos(request, table, qos_name, title, subtitle, ytitle, view_types, hour_flag, base_radix=1):
    begin_time = time.time()
    items = []

    try:
        (service_type, device_type, device_types,
            version, versions, begin_date, end_date) = get_filter_param_values(request, table)

        if device_type == "":
            raise NoDataError("No data between %s - %s in %s" % (begin_date, end_date, table))

        if version == "All":
            device_type_full = device_type
        else:
            device_type_full = '%s_%s' % (device_type, version)

        filterParams = FilterParams(table, service_type, device_type_full, begin_date, end_date)

        # process data from databases;
        if begin_date == end_date and hour_flag == True:
            data_by_hour = prepare_hour_data_of_single_Qos(
                filterParams, view_types, qos_name, base_radix)
            if data_by_hour is None:
                raise NoDataError(
                    "No hour data between %s - %s" % (begin_date, end_date))
            item = make_plot_item(data_by_hour, view_types,
                0, HOUR_XAXIS, title, subtitle, ytitle)
            items.append(item)
        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_daily_data_of_single_Qos(
                filterParams, days_region, view_types, qos_name, hour_flag, base_radix)
            if data_by_day is None:
                raise NoDataError(
                    "No daily data between %s - %s" % (begin_date, end_date))

            format_days_region = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
            item = make_plot_item(data_by_day, view_types, 0,
                format_days_region, title, subtitle, ytitle)
            items.append(item)

    except Exception, e:
        logger.info("query %s %s error: %s" % (str(table), qos_name, e))
        raise

    context = {}
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

    logger.info("query %s %s, cost: %s" %
                (str(table), qos_name, (time.time() - begin_time)))

    return context