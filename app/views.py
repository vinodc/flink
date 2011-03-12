from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core import serializers
from django.forms.models import modelformset_factory

from django.views.decorators.csrf import csrf_exempt

import json

from app.forms import *
from app.models import *
from app.decorators import *

# Logger:
from settings import logger
# To log, logger.debug('HELLO')
# or, logger.info('just some info here')
# or perhaps, logger.error('ERROR!!!')
# Logs are at logs/flink.log
# More info:
# http://docs.djangoproject.com/en/dev/topics/logging/

# Debugger:
# import ipdb


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
# Templates for creating a new posterboard should be within the
# display of something somewhere, and post to /posterboards
# Similar for people.

# Use the get_blogger decorator to make sure that blogger is a User
# object referring to the owner of the blog being accessed.
# This is defined in decorators.py
@handle_handlers
@get_blogger
def people_handler(request, blogger=None, format='html'):
    user = request.user

    # GET request with no specific user, so what is needed is a list of users.
    if request.method == 'GET' and blogger is None:
        bloggers = User.objects.filter(is_superuser__exact=False)
        data = {'bloggers': map(lambda b: 
                                {'username': b.username, 
                                 'full_name': b.get_full_name()},
                                bloggers)}
        if format == 'html':
            return render_to_response('people/index.html',data,
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
            if blogger.id == user.id:
                PosterboardFormSet = modelformset_factory(Posterboard)
                data['posterboard_formset'] = PosterboardFormSet()
            return render_to_response('people/show.html', data,
                                      context_instance=RequestContext(request))
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # DELETE request, to delete that specific blog and user. Error for now.
    elif request.method == 'DELETE' and blogger is not None and \
            (blogger.id == user.id and blogger.username == user.username):
        # Trying to delete themselves? Not handling it for now.
        data = {'blogger': 
                {'username': blogger.username,
                 'full_name': blogger.get_full_name()},
                'errors': 'User deletion not supported this way.'}
        if format == 'html':
            return render_to_response('people/show.html', data,
                                      context_instance=RequestContext(request))
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'errors': 'Invalid request'}
    if format == 'html':
        return render_to_response('people/index.html', error,
                                  context_instance=RequestContext(request))
    elif format == 'json':
        return HTTPResponse(json.dumps(error), mimetype='application/json',
                            status=400)

@handle_handlers
@get_blogger
@get_set
def sets_handler(request, blogger=None, set=None, format='html'):
    user = request.user
    # TODO
    return HTTPResponseNotFound()


@handle_handlers
@get_blogger
@get_posterboard
def posterboards_handler(request, blogger=None, posterboard=None,
                         format='html'):
    user = request.user
    data = {}

    # Extra check for redundancy. This is already handled in the decorator.
    if blogger is None:
        logger.info("Attempt to access PB without blogger o.O")
        return HTTPResponseForbidden('Please specify a blogger first.')

    # index
    if request.method == 'GET' and posterboard is None:
        if blogger.id == user.id:
            pbs = blogger.posterboard_set.all()    
        else:
            pbs = blogger.posterboard_set.filter(is_private=False).all()

        if format == 'html':
            return render_to_response('posterboards/index.html',
                                      {'blogger': blogger, 'posterboards': pbs}, 
                                      context_instance=RequestContext(request))
        elif format == 'json':
            data = serializers.serialize('json', pbs)
            return HTTPResponse(data, mimetype='application/json')

    # show
    elif request.method == 'GET' and posterboard is not None:
        if blogger.id != user.id and pb.is_private:
            return HTTPResponseForbidden('Private Posterboard.')

        if format == 'html':
            ElementFormSet = modelformset_factory(Element)
            e = ElementFormSet()
            return render_to_response('posterboards/show.html',
                                      {'blogger': blogger, 'posterboard': pb, 
                                       'element': e},
                                      context_instance=RequestContext(request))
        elif format == 'json':
            data = serializers.serialize('json', pb)
            return HTTPResponse(json.dumps(data), mimetype='application/json')
        
    # create
    elif request.method == 'POST':
        form = PosterboardForm(request.POST)
        if form.is_valid():
            # commit=False returns the model object but doesn't save it.
            posterboard = form.save(commit=False)
            # Do some stuff if necessary.
            # ...
            # Just demonstrating here how we can separately save the PB.
            posterboard.save()
            user.posterboard_set.add(posterboard)
            
            if format == 'html':
                # A redirect with this object will redirect to the url 
                # specified as the permalink in that model.
                # More info:
                # http://docs.djangoproject.com/en/dev/topics/http/shortcuts/#redirect
                return redirect(posterboard)
            elif format == 'json':
                data['message'] = 'Posterboard created successfully.'
                data['posterboard'] = serializers.serialize('json', posterboard)
                return HTTPResponse(json.dumps(data), mimetype='application/json')
        else:
            data['errors'] = 'Posterboard data isn\'t valid.'
            if format == 'html':
                return redirect(user, data)
            elif format == 'json':
                return HTTPResponseBadRequest(json.dumps(data), mimetype='application/json')

    # destroy
    elif request.method == 'DELETE' and posterboard is not None and \
            blogger.id == user.id:
        data = {'success': True}
        if format == 'html':
            return redirect(blogger)
        elif format == 'json':
            return HTTPResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'errors': 'Invalid request'}
    if format == 'html':
        return redirect(blogger)
    elif format == 'json':
        return HTTPResponse(json.dumps(error), mimetype='application/json',
                            status=400)

@handle_handlers
@get_blogger
@get_posterboard
@get_element
def elements_handler(request, blogger=None, posterboard=None, element=None,
                     format='html'):
    user = request.user

    # TODO
    return HTTPResponseNotFound()

