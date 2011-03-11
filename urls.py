from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from django.conf.urls.defaults import *
from django.conf import settings
import app.views as views
from app.models import *

from django.contrib import admin
admin.autodiscover()

posterboardpatterns= \
patterns('',
         url(r'^$', views.Posterboards.as_view(model=Posterboard)),
         url(r'^(?P<url_posterboard>[^/]+)/$', views.PosterboardInstance.as_view(model=Posterboard), name='posterboard'),
         )

userpatterns = \
patterns('',
         (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/accounts/'}),
         url(r'^(?P<user>[^/]+)/$', views.ProfileInstance.as_view(model=Profile), name='profile'),
         (r'^(?P<url_username>[^/]+)/posterboards/$', include(posterboardpatterns)))

urlpatterns = \
patterns('',
         url(r'^$', 'app.views.index'),
         (r'^app/', include(userpatterns)),
         (r'^admin/', include(admin.site.urls)),
         (r'^accounts/', include('allauth.urls')),
         #(r'^person/', include('account.person_urls')),
         )

# this allows you to access static file when DEBUG=True
urlpatterns += staticfiles_urlpatterns()
