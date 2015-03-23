"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.template import RequestContext
from datetime import datetime
import logging

logger = logging.getLogger("django.request")

def home(request):
    logger.debug("Qos request")
    return HttpResponse("BesTVQoS...")