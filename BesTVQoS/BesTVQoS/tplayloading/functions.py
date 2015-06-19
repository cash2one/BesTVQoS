# -*- coding: utf-8 -*-
import logging
import time

from django.db.models import Q
from common.views import get_default_values_from_cookie
from common.date_time_tool import today, get_day_of_day, get_days_region
from tplay.functions import NoDataError, FilterParams, HOUR_X_AXIS
from tplayloading.models import *

logger = logging.getLogger("django.request")
SERVICE_TYPES = ["B2B", "B2C"]

def get_device_types1(service_type, begin_date, end_date, min_rec):
    begin_time = time.time()
    q_conditions = Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    q_conditions = q_conditions & Q(Records__gte=min_rec)
    q_conditions = q_conditions & Q(VersionId__ServiceType=service_type)
    objs = TPlayloadingTitle.objects.filter(q_conditions).select_related('VersionId').distinct()
    type_set = set()
    for obj in objs:
            type_set.add(obj.VersionId.DeviceType)
                

    device_types = []
    device_types.extend(sorted(type_set))
    logger.info("get device type cost: %s" % ((time.time() - begin_time)))

    return device_types

def get_versions1(service_type, device_type, begin_date, end_date, min_rec):
    begin_time = time.time()
    q_conditions = Q(Date__gte=begin_date) & Q(Date__lte=end_date)
    q_conditions = q_conditions & Q(Records__gte=min_rec)
    q_conditions = q_conditions & Q(VersionId__ServiceType=service_type)
    q_conditions = q_conditions & Q(VersionId__DeviceType=device_type)
    objs = TPlayloadingTitle.objects.filter(q_conditions).select_related('VersionId').distinct()
    type_set = set()
    for obj in objs:
        if obj.VersionId.VersionType != 'All':
            type_set.add(obj.VersionId.VersionType)

    version_types = []
    if type_set:
        version_types.append('All')
        version_types.extend(sorted(type_set))

    logger.info("get version type cost: %s" % ((time.time() - begin_time)))

    return version_types

def get_loading_param_values(request):
    filters_map = get_default_values_from_cookie(request)
    service_type = request.GET.get("service_type", filters_map["st"]).encode("utf-8")
    device_type = request.GET.get("device_type", filters_map["dt"]).encode("utf-8")
    version = request.GET.get("version", filters_map["vt"]).encode("utf-8")
    begin_date = request.GET.get("begin_date", filters_map["begin"]).encode("utf-8")
    end_date = request.GET.get("end_date", filters_map["end"]).encode("utf-8")
    min_rec = request.GET.get("min_rec", '300')
    if not min_rec:
        min_rec = 300
    else:
        min_rec = int(min_rec)

    if begin_date >= str(today()):
        begin_date = str(get_day_of_day(-1))
        end_date = begin_date

    device_types = get_device_types1(service_type, begin_date, end_date, min_rec)
    if len(device_types) == 0:
        device_types = [""]
        device_type = ""

    if device_type not in device_types:
        device_type = device_types[0]

    versions = []
    try:
        versions = get_versions1(service_type, device_type, begin_date, end_date, min_rec)
    except:
        logger.info("get_versions({0}, {1}, {2}, {3}) failed.".format(
            service_type, device_type, begin_date, end_date))

    if len(versions) == 0:
        versions = [""]
        version = ""
    if version not in versions:
        version = versions[0]
    
    return service_type, device_type, device_types, version, \
        versions, begin_date, end_date, min_rec

# key_values: {1:[...], 2:[xxx], 3:[...]} sucratio of all viewtypes:  key
# is viewtype, lists contain each hour's data
def make_loading_item(key_values, keys, item_idx, x_axis, title, subtitle, y_title):
    item = dict()
    item["index"] = item_idx
    item["title"] = title
    item["subtitle"] = subtitle
    item["y_title2"] = y_title
    item["xAxis"] = x_axis
    item["t_interval"] = 1
    if len(x_axis) > 30:
        item["t_interval"] = len(x_axis) / 30

    series = []

    if "records" in key_values:
        yAxis = 0
        show_format = 'column'
        serie_item = '''{
                name: 'records',
                yAxis: %s,
                type: '%s',
                data: [%s]
            }'''%(yAxis, show_format, ",".join(['{0}'.format(v) for v in key_values['records']]))
        series.append(serie_item)

    for (i, desc) in keys:
        serie_item = '''{
            name: '%s',
            yAxis: 1,
            type: 'spline',
            data: [%s]
        }''' % (desc, ",".join(['{0}'.format(v) for v in key_values[i]]))
        series.append(serie_item)

    item["series"] = ",".join(series)

    return item

def prepare_hour_data(filter_params, version, choketype, view_types, pn_types):
    q_conditions = Q(ServiceType=filter_params.service_type)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(VersionType=version)
    version_id = VersionInfo.objects.get(q_conditions)

    q_conditions = Q(VersionId=version_id)
    q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions = q_conditions & Q(Hour__lt=24) & Q(ChokeType=choketype)
    q_conditions = q_conditions & Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)

    results = filter_params.table.objects.filter(q_conditions)
    view_type_hour = {}
    for row in results:
        for (pn, _) in pn_types:
            view_type_hour[(pn, row.Hour, row.ViewType)] = getattr(row, pn)

    records_hour = {}
    for row in results:
        records_hour[(row.Hour, row.ViewType)] = row.Records

    data_by_hour = {}
    for view_type in [view_type[0] for view_type in view_types]:
        display_data = {}
        if_show = False
        for (pn, _) in pn_types:
            display_data[pn] = []
            for hour in range(24):
                display_data[pn].append(view_type_hour.get((pn, hour, view_type), 0.0))
            if sum(display_data[pn]) > 0:
                if_show = True
        if if_show:
            display_data['records'] = []
            for hour in range(24):
                display_data['records'].append(records_hour.get((hour, view_type), 0))
            data_by_hour[view_type] = display_data

    return data_by_hour

def prepare_daily_data(filter_params, version, choketype, days_region, view_types, pn_types):
    q_conditions = Q(ServiceType=filter_params.service_type)
    q_conditions = q_conditions & Q(DeviceType=filter_params.device_type)
    q_conditions = q_conditions & Q(VersionType=version)
    version_id = VersionInfo.objects.get(q_conditions)

    q_conditions = Q(VersionId=version_id)
    q_conditions = q_conditions & Q(ISP='all') & Q(Area='all')
    q_conditions = q_conditions & Q(Hour=24) & Q(ChokeType=choketype)
    q_conditions = q_conditions & Q(Date__gte=filter_params.begin_date) & Q(Date__lte=filter_params.end_date)
    
    results = TPlayloadingInfo.objects.filter(q_conditions)
    view_type_date = {}
    for row in results:
        for (pn, _) in pn_types:
            view_type_date[(pn, str(row.Date), row.ViewType)] = getattr(row, pn)

    records_date = {}
    for row in results:
        records_date[(str(row.Date), row.ViewType)] = row.Records

    data_by_date = {}
    for view_type in [view_type[0] for view_type in view_types]:
        display_data = {}
        if_show = False
        for (pn, _) in pn_types:
            display_data[pn] = []
            for day in days_region:
                display_data[pn].append(view_type_date.get((pn, day, view_type), 0.0))
            if sum(display_data[pn]) > 0:
                if_show = True

        if if_show:
            display_data['records'] = []
            for day in days_region:
                display_data['records'].append(records_date.get((day, view_type), 0))
            data_by_date[view_type] = display_data

    return data_by_date

def process_tplayloading_qos(request, table, choketype, title, subtitle, y_title, view_types, pn_types):
    begin_time = time.time()
    items = []

    try:
        (service_type, device_type, device_types, version, versions, 
            begin_date, end_date, min_rec) = get_loading_param_values(request)
        if device_type == "":
            raise NoDataError("No data between {0} and {1} in tplayloading".format(begin_date, end_date))

        filter_params = FilterParams(table, service_type, device_type, begin_date, end_date)
        if begin_date == end_date:
            data_by_hour = prepare_hour_data(filter_params, version, choketype, view_types, pn_types)
            if data_by_hour is None:
                raise NoDataError("No hour data between {0} and {1} in tplayloading".format(begin_date, end_date))
            
            item_idx = 0
            for (view_type_idx, view_desc) in view_types:
                if view_type_idx not in data_by_hour:
                    continue
                item = make_loading_item(data_by_hour[view_type_idx], pn_types, item_idx, HOUR_X_AXIS,
                    title, "%s %s" % (subtitle, view_desc), y_title)
                items.append(item)
                item_idx += 1

        else:
            days_region = get_days_region(begin_date, end_date)
            data_by_day = prepare_daily_data(filter_params, version, choketype,
                days_region, view_types, pn_types)
            if data_by_day is None:
                raise NoDataError("No daily data between {0} and {1} in tplayloading".format(begin_date, end_date))

            format_days_region = ["%s%s" % (i[5:7], i[8:10]) for i in days_region]
            item_idx = 0
            for (view_type_idx, view_desc) in view_types:
                if view_type_idx not in data_by_day:
                    continue
                item = make_loading_item(data_by_day[view_type_idx], pn_types, item_idx, format_days_region, title,
                                      "%s %s" % (subtitle, view_desc), y_title)
                items.append(item)
                item_idx += 1

    except Exception, e:
        logger.info("query {0} {1} error: {2}".format(table.__name__, choketype, e))

    context = dict()
    context['default_service_type'] = service_type
    context['service_types'] = SERVICE_TYPES
    context['default_device_type'] = device_type
    context['device_types'] = device_types
    context['default_version'] = version
    context['versions'] = versions
    context['default_begin_date'] = str(begin_date)
    context['default_end_date'] = str(end_date)
    context['default_min_rec'] = "%s" % min_rec
    context['contents'] = items
    if len(items) > 0:
        context['has_data'] = True

    logger.info("query {0} {1} cost {2}".format(table.__name__, choketype, (time.time() - begin_time)))

    return context
