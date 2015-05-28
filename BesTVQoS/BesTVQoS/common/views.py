# -*- coding: utf-8 -*-

"""
Definition of views.
"""

import logging
import json

from django.shortcuts import render_to_response
from django.template import Context
from django.db import connection
from django.contrib.auth.decorators import login_required
# from common.navi import Navi
from common.date_time_tool import today

logger = logging.getLogger("django.request")


class HtmlTable:
    mtitle = "title"
    mheader = ["header"]
    msub = [['sub1'], ['sub2']]


def get_cell_width(num_characters):
    return int((1+num_characters) * 256)

# 
def write_xls(book, sheet, rowx, headings, data, heading_xf, data_xf):
    for colx, value in enumerate(headings):
        try:
            width = get_cell_width(len(value))
        except Exception, e:
            width = -1
        if width > sheet.col(colx).width:
            sheet.col(colx).width = width
        sheet.write(rowx, colx, value, heading_xf)

    for row in data:
        rowx+=1
        for colx, value in enumerate(row):
            try:
                width = get_cell_width(len(value))
            except Exception, e:
                width = -1
            if width > sheet.col(colx).width:
                sheet.col(colx).width = width
            sheet.write(rowx, colx, value, data_xf)

    return rowx


def write_remarks_to_xls(book, sheet, rowx, data, data_xf):
    for value in data:
        sheet.write(rowx, 0, value, data_xf)
        rowx+=1

    return rowx

@login_required
def home(request):
    return render_to_response('index.html', Context())

@login_required
def p_home(request):
    return render_to_response('home.html', Context())

@login_required
def m_home(reuest):
    context = {}
    context["is_mobile"] = True
    context["top_title"] = "BesTV QoS Monitor"
    #context["navi"] = Navi().get_sub_items()

    return render_to_response('m_navi_menu.html', context)

@login_required
def navi(request, target_url=""):
    if target_url:
        navi = Navi()
        navi_path = navi.get_path(request.path)
        context = {}
        context["navi"] = navi.get_sub_items(request.path)
        context["is_mobile"] = True
        context["top_title"] = navi_path[-1].name
        context["show_topbar"] = True
        context["path"] = navi_path[:-1]
        return render_to_response('m_navi_menu.html', context)
    else:
        return m_home(request)


def get_default_values_from_cookie(request):
    filter_map = json.loads('{"st":"B2C","dt":"","vt":"","begin":"%s","end":"%s"}' % (
        today(), today()))
    try:
        filter_map = json.loads(request.COOKIES["bestvFilters"])
        if("st" not in filter_map or "dt" not in filter_map or "vt" not in filter_map or
                "begin" not in filter_map or "end" not in filter_map):
            raise Exception()
    except:
        logger.info("Loads Cookie['bestvFilters'] failed! ")

    return filter_map


def set_default_values_to_cookie(response, context):
    response.set_cookie("bestvFilters",
                        json.dumps({"st": context["default_service_type"],
                                    "dt": context["default_device_type"],
                                    "vt": context["default_version"],
                                    "begin": context['default_begin_date'],
                                    "end": context['default_end_date']}),
                        max_age=30000)