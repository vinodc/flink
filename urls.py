from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$',   'app.views.index'),

    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('allauth.urls')),
    #(r'^person/', include('account.person_urls')),
)

# this allows you to access static file when DEBUG=True
urlpatterns += staticfiles_urlpatterns()
