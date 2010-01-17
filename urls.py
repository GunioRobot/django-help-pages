from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^', include('help.urls')),

    #Django admin required
    (r'^admin/', include(admin.site.urls)),
)
