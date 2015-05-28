#!/usr/bin/env python
#coding:UTF-8

from django.conf.urls import patterns, url

urlpatterns = patterns('tplay.views',
    # url(r"show_fbuffer_sucratio/get_version", "get_version",),
    # url(r"show_fbuffer_sucratio/get_device_type", "get_device_type",),
    # url(r"show_fbuffer_sucratio1/", "show_fbuffer_sucratio1",),
    url(r'get_device_type$', "get_device_type"),
    url(r'get_version$', "get_version"),
    url(r'show_playing_trend$', 'show_playing_trend'),
    url(r'show_playing_daily$', 'show_playing_daily'),
    url(r'show_play_time$', 'show_play_time'),
    url(r'show_fbuffer_sucratio$', 'show_fbuffer_sucratio'),
    url(r'show_fbuffer_time$', 'show_fbuffer_time'),
    url(r'show_fluency$', 'show_fluency'),
    url(r'show_fluency_pratio$', 'show_fluency_pratio'),
    url(r'show_fluency_allpratio$', 'show_fluency_allpratio'),
    url(r'show_fluency_avgcount$', 'show_fluency_avgcount'),

    url(r'show_3sratio$', 'show_3sratio'),
    url(r'show_avg_pcount$', 'show_avg_pcount'),
    url(r'show_avg_ptime$', 'show_avg_ptime'),
)