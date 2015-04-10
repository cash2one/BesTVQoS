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
    url(r'^update/realtime/base$', 'store.views.baseinfo'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
