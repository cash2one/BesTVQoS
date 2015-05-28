"""
Definition of urls for BesTVQoS.
"""

from datetime import datetime
from django.conf.urls import patterns, url
from common.forms import BootstrapAuthenticationForm

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', 'common.views.home', name='home'),
    url(r'^p/$', 'common.views.p_home'),
    url(r'^m/$', 'common.views.m_home'),
    url(r'^navi/(?P<target_url>\w*)', 'common.views.navi'),
    # url(r'^((?P<dev>m)/)?get_device_type$',
    #     'tplay.views.get_device_type'),
    # url(r'^((?P<dev>m)/)?get_version$',
    #     'tplay.views.get_version'),

    # url(r'^((?P<dev>m)/)?show_playing_daily$',
    #     'tplay.views.show_playing_daily'),
    # url(r'^((?P<dev>m)/)?show_playing_trend$',
    #     'tplay.views.show_playing_trend'),

    # url(r'^((?P<dev>m)/)?show_play_time$',
    #     'tplay.fbuffer_views.show_play_time'),

    # url(r'^((?P<dev>m)/)?show_fbuffer_sucratio$',
    #     'tplay.fbuffer_views.show_fbuffer_sucratio'),
    # url(r'^((?P<dev>m)/)?show_fbuffer_time$',
    #     'tplay.fbuffer_views.show_fbuffer_time'),

    # url(r'^((?P<dev>m)/)?show_fluency$',
    #     'tplay.fbuffer_views.show_fluency'),
    # url(r'^((?P<dev>m)/)?show_fluency_pratio$',
    #     'tplay.fbuffer_views.show_fluency_pratio'),
    # url(r'^((?P<dev>m)/)?show_fluency_allpratio$',
    #     'tplay.fbuffer_views.show_fluency_allpratio'),
    # url(r'^((?P<dev>m)/)?show_fluency_avgcount$',
    #     'tplay.fbuffer_views.show_fluency_avgcount'),
    #
    # url(r'^((?P<dev>m)/)?show_3sratio$',
    #     'tplay.fbuffer_views.show_3sratio'),
    # url(r'^((?P<dev>m)/)?show_avg_pcount$',
    #     'tplay.fbuffer_views.show_avg_pcount'),
    # url(r'^((?P<dev>m)/)?show_avg_ptime$',
    #     'tplay.fbuffer_views.show_avg_ptime'),

    url(r'^((?P<dev>m)/)?day_reporter$',
        'tplay.report_views.pre_day_reporter'),    
    url(r'^((?P<dev>m)/)?display_daily_reporter$',
        'tplay.report_views.display_daily_reporter'),
    url(r'^((?P<dev>m)/)?download_daily_reporter$',
        'tplay.report_views.download_daily_reporter'),
    url(r'^((?P<dev>m)/)?week_reporter$',
        'tplay.report_views.pre_day_reporter'),

    # log analyze
    url(r'^((?P<dev>m)/)?show_server_list$',
        'loganalyze.server_views.show_server_list'),
    url(r'^((?P<dev>m)/)?export_server_list$',
        'loganalyze.server_views.export_server_list'),
    url(r'^((?P<dev>m)/)?show_server_detail$',
        'loganalyze.server_views.show_server_detail'),
    url(r'^((?P<dev>m)/)?get_server_url_distribute$',
        'loganalyze.server_views.get_server_url_distribute'),
    url(r'^((?P<dev>m)/)?get_ip_list$',
        'loganalyze.server_views.get_ip_list'),

    # cdn Mon
    url(r'^((?P<dev>m)/)?show_ms_error$',
        'cdnMon.views.show_ms_error'),
    url(r'^((?P<dev>m)/)?show_tsdelay$',
        'cdnMon.views.show_tsdelay'),
    url(r'^((?P<dev>m)/)?show_cdn_detail$',
        'cdnMon.views.show_cdn_detail'),

    # data interface
    url(r'^update/playprofile$', 'tplay.update_views.playprofile'),
    url(r'^update/playinfo$', 'tplay.update_views.playinfo'),
    url(r'^update/playtime$', 'tplay.update_views.playtime'),
    url(r'^update/fbuffer$', 'tplay.update_views.fbuffer'),
    url(r'^update/fluency$', 'tplay.update_views.fluency'),
    url(r'^update/bestv3Sratio$', 'tplay.update_views.bestv3Sratio'),
    url(r'^update/bestvavgpchoke$', 'tplay.update_views.bestvavgpchoke'),

    # realtime data interface
    url(r'^update/realtime/base$', 'realtime.views.baseinfo'),

    # flush redis cache
    url(r'^flushdb2$', 'common.views.flushdb2'),

    url(r'^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tplay/', include("tplay.urls")),
)
