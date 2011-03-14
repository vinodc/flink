from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

elementpatterns = patterns(
    'app.views',
    url(r'^$', 'elements_handler', name='elements_url'),
    url(r'^(?P<element_id>\d+)/?(\.(?P<format>(json|html)))?$',
        'elements_handler', name='element_url'),
    )

posterboardpatterns = patterns(
    'app.views',
    url(r'^$', 'posterboards_handler', name='posterboards_url'),
    # Get a particular set of posterboards.
    url(r'^sets/?(\.(?P<format>(json|html)))?$', 'sets_handler',
        name='sets_url'),
    url(r'^sets/(?P<set>\d+)/?(\.(?P<format>(json|html)))?$', 
        'sets_handler', name='set_url'),
    url(r'^(?P<posterboard>[^./]+)/?(\.(?P<format>(json|html)))?$',
        'posterboards_handler', name='posterboard_url'),
    (r'^(?P<posterboard>[^./]+)/elements(/|/?\.(?P<format>(json|html))$)',
     include(elementpatterns)),
    )

peoplepatterns = patterns(
    'app.views',
    url(r'^(\.(?P<format>(json|html)))?$', 'people_handler', name='people_url'),
    url(r'^(?P<blogger>[^./]+)/?(\.(?P<format>(json|html)))?$',
        'people_handler', name='person_url'),
    (r'^(?P<blogger>[^./]+)/posterboards(/|/?\.(?P<format>(json|html))$)',
     include(posterboardpatterns)),
    )

profilepatterns = patterns(
    'app.views',
    url(r'^$', 'profile_handler', name='user_settings'),                       
    )

urlpatterns = patterns(
    '',
    (r'^$', 'app.views.index'),
    (r'^people[/$]', include(peoplepatterns)),
    (r'^admin[/$]', include(admin.site.urls)),
    (r'^profile[/$]', include(profilepatterns)),
    (r'^accounts[/$]', include('allauth.urls')),

    #(r'^person/', include('account.person_urls')),
    )

# this allows you to access static file when DEBUG=True
urlpatterns += staticfiles_urlpatterns()
