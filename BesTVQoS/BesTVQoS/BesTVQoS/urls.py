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

    url(r'^((?P<dev>m)/)?show_playing_daily$',
        'tplay.views.show_playing_daily'),

    # data interface
    url(r'^update/playprofile$', 'tplay.update_views.playprofile'),
    url(r'^update/playinfo$', 'tplay.update_views.playinfo'),
    url(r'^update/playtime$', 'tplay.update_views.playtime'),
    url(r'^update/fbuffer$', 'tplay.update_views.fbuffer'),
    url(r'^update/fluency$', 'tplay.update_views.fluency'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
