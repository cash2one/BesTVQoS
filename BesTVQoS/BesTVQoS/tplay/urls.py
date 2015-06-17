#!/usr/bin/env python
#coding:UTF-8

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'tplay.views',

    url(r'show_version_analyze', 'show_version_analyze'),
    url(r'get_device_type$', 'get_device_type'),
    url(r'get_version$', 'get_version'),
    url(r'show_playing_trend$', 'show_playing_trend'),
    url(r'show_playing_stat$', 'show_playing_stat'),
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

    url(r'get_users/(?P<date_str>.*)$', 'get_one_day_users')
)
