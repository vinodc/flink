from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from django.conf.urls.defaults import *
from django.conf import settings
from settings import MEDIA_SERVER, MEDIA_URL
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

#import django_cron
#django_cron.autodiscover()

elementpatterns = patterns(
    'app.views',
    url(r'^$', 'elements_handler', name='elements_url'),
    #url(r'^(\.(?P<format>(json|html)))?$', 'elements_handler', name='elements_url'),
    url(r'^(?P<element>\d+)/?(\.(?P<format>(json|html)))?$',
        'elements_handler', name='element_url'),
    )

posterboardpatterns = patterns(
    'app.views',
    url(r'^$', 'posterboards_handler', name='posterboards_url'),
    url(r'^new[/$]', 'new_posterboards_handler'),
    
    # Get a particular set of posterboards.    
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
    url(r'^(?P<blogger>[^./]+)/homepages/(?P<homepageid>\d+)/?(\.(?P<format>(json|html)))?$',
         'people_handler', name='person_url'),
    (r'^(?P<blogger>[^./]+)/posterboards(/|/?\.(?P<format>(json|html))$)',
     include(posterboardpatterns)),
    )

profilepatterns = patterns(
    'app.views',
    url(r'^(\.(?P<format>(json|html)))?$', 'profile_handler', name='profile_url'),
    url(r'^settings/?(\.(?P<format>(json|html)))?$', 'settings_handler', name='profile_url'),
    )

urlpatterns = patterns(
    '',
    (r'^$', 'app.views.index'),
    (r'^(people|users)[/$]', include(peoplepatterns)),
    (r'^admin[/$]', include(admin.site.urls)),
    (r'^profile[/$]', include(profilepatterns)),
    (r'^accounts[/$]', include('allauth.urls')),
    (r'^'+ MEDIA_URL[1:] + '(?P<media>.*)$', redirect_to, 
     {'url': MEDIA_SERVER['PROTOCOL'] + '://' +
             MEDIA_SERVER['HOST'] +':'+ 
             str(MEDIA_SERVER['PORT']) + '/%(media)s'})

    #(r'^person/', include('account.person_urls')),
    )

# this allows you to access static file when DEBUG=True
urlpatterns += staticfiles_urlpatterns()

# media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

