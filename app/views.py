from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

import json

# Debugger:
# import ipdb


@login_required
def index(request):
    return render_to_response('index.html', {
        }, context_instance=RequestContext(request))
