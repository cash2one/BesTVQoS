#!/usr/bin/env python
#coding:UTF-8

from django.conf.urls import patterns, url

urlpatterns = patterns('tplay.views',
    url(r"show_fbuffer_sucratio/get_version", "get_version",),
    url(r"show_fbuffer_sucratio/get_device_type", "get_device_type",),
    url(r"show_fbuffer_sucratio/", "show_fbuffer_sucratio",),
)