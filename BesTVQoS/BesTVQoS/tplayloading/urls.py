from django.conf.urls import patterns, url

urlpatterns = patterns('tplayloading.views', 
    url(r'update/info$', 'update_info'),
    url(r'update/title$', 'update_title'),
    url(r'get_device_type$', 'get_device_type1'),
    url(r'get_version_type$', 'get_version1'),
    url(r'show_stuck$', 'show_stuck'), 
    url(r'show_dbuffer$', 'show_dbuffer'),
)