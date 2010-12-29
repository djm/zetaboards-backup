from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    MEDIA_URL = settings.MEDIA_URL.strip('/')
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % MEDIA_URL, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT,
          'show_indexes': True})
)
