from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from djangorestframework.modelresource import ModelResource, RootModelResource
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import json

from app.models import *

# Debugger:
# import ipdb


@login_required
def index(request):
    return render_to_response('index.html', {
        }, context_instance=RequestContext(request))

#-----------------------
# Django REST stuff
#-----------------------

PROFILEFIELDS = ('absolute_url')
POSTERBOARDFIELDS = ('title', 'is_private', 'display_set', 'display_position',
                     'snapshot_position', 'snapshot_width', 'snapshot_height',
                     'snapshot', 'absolute_url')

class Posterboards(RootModelResource):
    model = Posterboard
    anon_allowed_methods = ('GET')
    allowed_methods = ('GET', 'POST')
    fields = POSTERBOARDFIELDS

class PosterboardInstance(ModelResource):
    model = Posterboard
    anon_allowed_methods = ('GET')
    allowed_methods = ('GET', 'PUT', 'DELETE')
    fields = POSTERBOARDFIELDS


class ProfileInstance(ModelResource):
    model = Profile
    allowed_methods = ('GET', 'PUT', 'DELETE')
    fields = PROFILEFIELDS
