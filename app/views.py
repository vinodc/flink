from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core import serializers

from django.views.decorators.csrf import csrf_exempt

import json

from app.forms import *
from app.models import *
from app.decorators import *

# Debugger:
# import ipdb

# Logging:
# This should log to log/flink.log
import logging
logger = logging.getLogger()
#logger.info("HELLO")


# The @login_required decorator makes it necessary for the user to have logged
# in first.
# @login_required
def index(request):
    return render_to_response('index.html', {
        }, context_instance=RequestContext(request))

# Follow the REST philosophy that:
# GET /posterboards - index of all PBs (for that user)
# POST /posterboards - create new PB
# GET /posterboards/X/ - show a PB with id X
# PUT /posterboards/X/ - update PB X
# DELETE /posterboards/X/ - delete PB X
# Similar for people:

# Use the get_blogger decorator to make sure that blogger is a User
# object referring to the owner of the blog being accessed.
# This is defined in decorators.py
@get_blogger
def people_handler(request, blogger=None, format='html'):
    user = request.user
    if format is None: format = 'html' 

    # GET request with no specific user, so what is needed is a list of users.
    if request.method == 'GET' and blogger is None:
        bloggers = User.objects.filter(is_superuser__exact=False)
        data = {'bloggers': map(lambda b: 
                                {'username': b.username, 
                                 'full_name': b.get_full_name()}, \
                                    bloggers)}
        if format == 'html':
            return render_to_response('people/index.html',data, \
                                          context_instance=RequestContext(request))
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # GET request with a specific user, so show that user's blog.
    elif request.method == 'GET' and blogger is not None:
        data = {'blogger': 
                {'username': blogger.username, 
                 'full_name': blogger.get_full_name()
                 }
                }
        if format == 'html':
            return render_to_response('people/show.html', data, \
                                          context_instance=RequestContext(request))
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # DELETE request, to delete that specific blog and user. Error for now.
    elif request.method == 'DELETE' and blogger is not None \
            and (blogger.id == user.id and blogger.username == user.username):
        # Trying to delete themselves? Not handling it for now.
        data = {'blogger': 
                {'username': blogger.username,
                 'full_name': blogger.get_full_name()},
                'error': 'User deletion not supported this way.'}
        if format == 'html':
            return render_to_response('people/show.html', data, \
                                          context_instance=RequestContext(request))
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'error': 'Invalid request'}
    if format == 'html':
        return render_to_response('people/index.html', error, \
                                      context_instance=RequestContext(request))
    elif format == 'json':
        return HTTPResponse(json.dumps(error), mimetype='application/json', \
                                status=400)


@get_blogger
#@get_posterboard #TODO
def posterboards_handler(request, blogger=None, posterboard=None):
    # TODO
    return HTTPResponseNotFound()


@get_blogger
#@get_posterboard #TODO
#@get_element #TODO
def elements_handler(request, blogger=None, posterboard=None, element=None):
    # TODO
    return HTTPResponseNotFound()

