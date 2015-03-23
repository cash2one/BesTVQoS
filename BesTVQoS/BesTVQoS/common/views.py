"""
Definition of views.
"""

# from django.shortcuts import render
# from django.http import HttpRequest
# from django.http import HttpResponse
# from django.template import RequestContext
# from datetime import datetime
from django.shortcuts import render_to_response
from django.template import Context
from navi import Navi
import logging

logger = logging.getLogger("django.request")


def home(request):
    logger.debug("Qos request")
    return render_to_response('home.html', Context())


def m_home(reuest):
    context = {}
    context["is_mobile"] = True
    context["top_title"] = "Funtv QoS Monitor"
    context["navi"] = Navi().get_sub_items()

    return render_to_response('m_navi_menu.html', context)


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
