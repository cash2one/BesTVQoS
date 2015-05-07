"""
Definition of urls for BesTVQoSStore.
"""

from datetime import datetime
from django.conf.urls import patterns, url

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # data interface
    url(r'^update/playprofile$', 'store.views.playprofile'),
    url(r'^update/playinfo$', 'store.views.playinfo'),
    url(r'^update/playtime$', 'store.views.playtime'),
    url(r'^update/fbuffer$', 'store.views.fbuffer'),
    url(r'^update/fluency$', 'store.views.fluency'),
    url(r'^update/bestv3Sratio$', 'store.views.bestv3Sratio'),
    url(r'^update/bestvavgpchoke$', 'store.views.bestvavgpchoke'),

    # realtime data interface
    url(r'^update/realtime/base$', 'realtime.views.baseinfo'),

    # serverlog
    url(r'^update/log/respcode$', 'logStore.views.respcode'),
    url(r'^update/log/urlinfo$', 'logStore.views.urlinfo'),
    url(r'^update/log/respdelay$', 'logStore.views.respdelay'),
    url(r'^update/log/reqdelay$', 'logStore.views.reqdelay'),

    # cdn Monitor
    url(r'^update/mon/mserror$', 'cdnMon.views.ms_error_info'),
    url(r'^update/mon/ts_delay$', 'cdnMon.views.ts_delay'),
    url(r'^update/mon/province_geo$', 'cdnMon.views.province_geo'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
