"""
Definition of urls for BesTVQoS.
"""

# from datetime import datetime
from django.conf.urls import patterns, url

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', 'common.views.home'),
    url(r'^m/$', 'common.views.m_home'),
    url(r'^navi/(?P<target_url>\w*)', 'common.views.navi'),
    url(r'^((?P<dev>m)/)?get_device_type$',
        'common.views.get_device_type'),

    url(r'^((?P<dev>m)/)?show_playing_daily$',
        'tplay.views.show_playing_daily'),
    url(r'^((?P<dev>m)/)?show_playing_trend$',
        'tplay.views.show_playing_trend'),

    url(r'^((?P<dev>m)/)?show_play_time$',
        'tplay.fbuffer_views.show_play_time'),

    url(r'^((?P<dev>m)/)?show_fbuffer_sucratio$',
        'tplay.fbuffer_views.show_fbuffer_sucratio'),
    url(r'^((?P<dev>m)/)?show_fbuffer_time$',
        'tplay.fbuffer_views.show_fbuffer_time'),

    url(r'^((?P<dev>m)/)?show_fluency$',
        'tplay.fbuffer_views.show_fluency'),
    url(r'^((?P<dev>m)/)?show_fluency_pratio$',
        'tplay.fbuffer_views.show_fluency_pratio'),
    url(r'^((?P<dev>m)/)?show_fluency_allpratio$',
        'tplay.fbuffer_views.show_fluency_allpratio'),
    url(r'^((?P<dev>m)/)?show_fluency_avgcount$',
        'tplay.fbuffer_views.show_fluency_avgcount'),


    # data interface
    url(r'^update/playprofile$', 'tplay.update_views.playprofile'),
    url(r'^update/playinfo$', 'tplay.update_views.playinfo'),
    url(r'^update/playtime$', 'tplay.update_views.playtime'),
    url(r'^update/fbuffer$', 'tplay.update_views.fbuffer'),
    url(r'^update/fluency$', 'tplay.update_views.fluency'),
    url(r'^update/bestv3Sratio$', 'tplay.update_views.bestvavgpchoke'),
    url(r'^update/bestvavgpchoke$', 'tplay.update_views.bestvavgpchoke'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
