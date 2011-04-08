from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import render_to_response, redirect, render
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.http import *
from django.conf import settings
from django.core import serializers
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.views.decorators.csrf import csrf_exempt

import sys
import json
from datetime import datetime 

from app.forms import PosterboardForm, ImageStateForm, StateForm, BlogSettingsForm, \
    ElementForm, TextStateForm, AudioStateForm, VideoStateForm
from app.models import Posterboard, BlogSettings, Element, State, \
    ImageState, TextState, AudioState, VideoState
from app.decorators import get_blogger, get_element, get_posterboard, \
    get_set, handle_handlers, get_blogger_settings

# Logger:
from settings import logger
# To log, logger.debug('HELLO')
# or, logger.info('just some info here')
# or perhaps, logger.error('ERROR!!!')
# Logs are at logs/flink.log
# More info:
# http://docs.djangoproject.com/en/dev/topics/logging/

from app.lib import title_to_path, jsonload

# Debugger:
#import ipdb

# Error
def ErrorResponse(data, format):
    if format == 'html':
        return HttpResponse(str(data), status=400)
    elif format == 'json':
        return HttpResponse(json.dumps(data), mimetype='application/json', status=400)


# The @login_required decorator makes it necessary for the user to have logged
# in first.
# @login_required
def index(request):
    return render_to_response('index.html', {
        }, context_instance=RequestContext(request))

@login_required
@get_blogger
@csrf_exempt
def new_posterboards_handler(request, blogger=None, format=None):
    return render_to_response('posterboards/new.html',{},
                              context_instance=RequestContext(request))
                              
@handle_handlers
@login_required
def settings_handler(request, format='html'):
    user = request.user
    blogsettingsform = BlogSettingsForm()
    
    if request.method == 'GET':
        data = {'profile':
                {'username': user.username,
                 'email': user.email
                 },
                'blogsettingsform': blogsettingsform,
                }
        
        if format=='html':
            return render_to_response('profile/edit_settings.html',data,
                                  context_instance=RequestContext(request))
        elif format=='json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    error = {'errors': 'Invalid request'}
    return ErrorResponse(error, format)
    
@handle_handlers
@login_required
def profile_handler(request, format='html'):
    current_user = request.user
    
    #check to make sure that a BlogSettings object has been crated for the user
    try:
	blogsettings = current_user.blogsettings
    except:
	blogsettings = BlogSettings(user=current_user)
	blogsettings.save()
                
    if request.method == 'GET':
        data = {'profile':
                {'username': current_user.username,
                 'email': current_user.email,
                 'gridsize': blogsettings.grid_size,
                 },
                }
                
        if format=='html':
            return render_to_response('profile/index.html',data,
                                  context_instance=RequestContext(request))
        elif format=='json':
            return HttpResponse(json.dumps(data), mimetype='application/json')
    
    elif request.method == 'POST':
        data = {'profile':
                {'username': current_user.username,
                 'email': current_user.email,
                 'old gridsize': blogsettings.grid_size,
                 },
                }
        #so at this point: we got the form from the edit_settings page and now we'll
        #use it to save it to the user's settings object
        settingsForm = BlogSettingsForm(request.POST, instance=blogsettings)
        if settingsForm.is_valid():
            settingsForm.save()
            data['message'] = 'New grid size is: ' + str(blogsettings.grid_size)
        else:
            error = {'errors': 'BlogSettingsFrom did not validate!'}
    	    return ErrorResponse(error, format)
          
        if format=='html':
            return render_to_response('profile/index.html',data,
                                  context_instance=RequestContext(request))
        elif format=='json':
            return HttpResponse(json.dumps(data), mimetype='application/json')
            
    error = {'errors': 'Invalid request'}
    return ErrorResponse(error, format)
    

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
@get_blogger_settings
def people_handler(request, blogger=None, homepageid=None, format='html', settings=None):
    user = request.user
    # GET request with no specific user, so what is needed is a list of users.
    if request.method == 'GET' and blogger is None:
        bloggers = User.objects.filter(is_superuser__exact=False)
        data = {'bloggers': map(lambda b:
                                {'first_name': b.first_name,
                                 'last_name': b.last_name,
                                 'username': b.username,
                                 'full_name': b.get_full_name()},
                                bloggers)}
        if format == 'html':
            return render_to_response('people/index.html',data,
                                      context_instance=RequestContext(request))
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # GET request with a specific user, so show that user's blog.
    elif request.method == 'GET' and blogger is not None:
        data = {'blogger':
                {'first_name': blogger.first_name,
                 'last_name': blogger.last_name,
                 'username': blogger.username,
                 'full_name': blogger.get_full_name()
                 },
                'settings':
                {'grid_size': settings.grid_size,
                 'blog_title': settings.blog_title
                 },
                }
        if blogger.id == user.id:
            pbs = blogger.posterboard_set
        else:
            pbs = blogger.posterboard_set.filter(private=False)
        pbs = pbs.filter(is_user_home_page=True).order_by('-created_at').all()

        if len(pbs) < 1:
            # Not a single homepage?! Create one.
            posterboard = Posterboard()
            posterboard.user = blogger
            posterboard.title = "userhomepage"
            posterboard.is_user_home_page = True
            posterboard.full_clean()
            posterboard.save()
        elif homepageid is None:
            posterboard = pbs[0]
        else:
            # This isn't really the posterboad, it's an array 
            # that should have it as the only element.
            # So it is [<posterboard>], not <posterboard>
            posterboard = pbs.filter(id=homepageid)
            if len(posterboard) == 0:
                posterboard = pbs[0]
            else:
                posterboard = posterboard[0]
            
        element_data = []
        for e in posterboard.element_set.all():
            sset = e.state_set.all()
            sset = list(sset[:1])
            s = None
            if sset:
                s = sset[0]
            ts = None
            if s is not None:
                type = e.type
                if type == 'image':
                    ts = s.imagestate
                else:
                    logger.debug(u"Can't get type state for type %s" % type)
            element_data.append(jsonload(serializers.serialize('json', [e, s, ts])))
        data['element_data'] = element_data

        #logger.debug('Element data passed to posterboard/show: '+ str(data['element_data'])) 
        #logger.debug('a random field: ' + data['element_data'][0][0]['fields']['type'])                   

        # TODO: pbs is an array of posterboards.

        if format == 'html':
            return render_to_response('people/show.html',
                                      {'blogger': blogger,
                                       'userhomepages': pbs,
                                       'posterboard': posterboard,
                                       'element_data': data['element_data'],
                                       'blog_owner': blogger.id == user.id},
                                      context_instance=RequestContext(request))
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')
        
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
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'errors': 'Invalid request'}
    if format == 'html':
        return render_to_response('people/index.html', error,
                                  context_instance=RequestContext(request))
    elif format == 'json':
        return HttpResponse(json.dumps(error), mimetype='application/json',
                            status=400)


@handle_handlers
@get_blogger
@get_set
def sets_handler(request, blogger=None, set=None, format='html'):
    user = request.user
    # TODO
    return HttpResponseNotFound()


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
        return HttpResponseForbidden('Please specify a blogger first.')

    # index
    if request.method == 'GET' and not request.GET.has_key('_action') and posterboard is None:
        if blogger.id == user.id:
            pbs = blogger.posterboard_set.filter(is_user_home_page=False).all()
        else:
            pbs = blogger.posterboard_set.filter(private=False,is_user_home_page=False).all()

        if format == 'html':
            return render_to_response('posterboards/index.html',
                                      {'blogger': blogger, 'posterboards': pbs},
                                      context_instance=RequestContext(request))
        elif format == 'json':
            data['pb_ids'] = []
            for pb in pbs:
                data['pb_ids'].append(pb.id)
            # Serialize object .. then get actual data structure out of serialized string
            return HttpResponse(data, mimetype='application/json')

    # show
    elif request.method == 'GET' and not request.GET.has_key('_action') and posterboard is not None:
        if blogger.id != user.id and posterboard.private:
            return HttpResponseForbidden('Private Posterboard.')
        elif posterboard.is_user_home_page:
            return HttpResponseRedirect('/people/'+blogger.username+'/homepages/'+str(posterboard.id)+'/')

        data['converting'] = False
        element_data = []
        for e in posterboard.element_set.all():
            sset = e.state_set.all()
            sset = list(sset[:1])
            s = None
            if sset:
                s = sset[0]
            ts = None
            if s is not None:
                type = e.type
                if type == 'image':
                    ts = s.imagestate
                elif type == 'audio':
                    ts = s.audiostate
                elif type == 'video':
                    ts = s.videostate
                    if( ts.original_video.name[-3:] != 'ogv' and ts.original_video.name[-3:] != 'ogg' and
                       (datetime.now() - ts.created_at).seconds < settings.CONVERSION_TIME):
                        # Don't want to display the video before conversion safely over.
                        data['converting'] = True
                        continue
                elif type == 'text':
                    ts = s.textstate
                else:
                    logger.debug(u"Can't get type state for type %s" % type)
            if settings.DEBUG:
                logger.info("\nSerializing: "+ str(s.__dict__) + str(e.__dict__) + str(ts.__dict__))
                logger.info("\nSerialized: "+ serializers.serialize('json', [e, s, ts]))
            element_data.append(jsonload(serializers.serialize('json', [e, s, ts])))
        data['element_data'] = element_data
        if settings.DEBUG:
            logger.info("\nElement data: "+ str(element_data))                    

        #logger.debug('Element data passed to posterboard/show: '+ str(data['element_data'])) 
        #logger.debug('a random field: ' + data['element_data'][0][0]['fields']['type'])                   

        if format == 'html':
            return render_to_response('posterboards/show.html',
                                      {'blogger': blogger,
                                        'posterboard': posterboard,
                                        'converting': data['converting'],
                                        'element_data': data['element_data'],
                                        'blog_owner': blogger.id == user.id},
                                      context_instance=RequestContext(request))
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # create, make sure to check user.id as only logged in user can create new posterboard
    elif user.id and request.method == 'POST':
        pbForm = PosterboardForm(request.POST)
        if pbForm.data['title'] is None or pbForm.data['title'] == '':
            pbForm.data['title'] = 'userhomepage'
        if pbForm.is_valid():
            # commit=False creates and returns the model object but doesn't save it.
            # Remove it if unnecessary.
            posterboard = pbForm.save(commit=False)
            try:
                posterboard.user = user
                posterboard.full_clean()
                posterboard.save()
            except ValidationError, e:
                return ErrorResponse(str(e), format)
            except IntegrityError, e:
                return ErrorResponse(str(e), format)
            except:
                return ErrorResponse(sys.exc_info()[0], format)
            
            if format == 'html':
                # A redirect with this object will redirect to the url
                # specified as the permalink in that model.
                # More info:
                # http://docs.djangoproject.com/en/dev/topics/http/shortcuts/#redirect
                if not posterboard.is_user_home_page:
                    return redirect('/people/'+user.username+'/posterboards/'+posterboard.title_path+'/')
                else:
                    return redirect('/people/'+user.username)
            elif format == 'json':
                data['message'] = 'Posterboard created successfully.'
                data['posterboard-id'] = posterboard.id
                data['posterboard-path'] = posterboard.title_path
                return HttpResponse(json.dumps(data), mimetype='application/json')
        else:
            data['errors'] = 'Posterboard data isn\'t valid: '
            data['errors'] += str(pbForm.errors)
            return ErrorResponse(data['errors'], format)


    # destroy
    elif request.method == 'GET' and request.GET.has_key('_action') and \
    request.GET['_action'] == 'delete' and posterboard is not None and blogger.id == user.id:
        posterboard.delete()
        if format == 'html':
            return redirect(blogger)
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'errors': 'Invalid request'}
    if format == 'html':
        return redirect(blogger)
    elif format == 'json':
        return HttpResponse(json.dumps(error), mimetype='application/json',
                            status=400)

@handle_handlers
@get_blogger
@get_posterboard
@get_element
def elements_handler(request, blogger=None, posterboard=None, element=None,
                     format='html'):
    user = request.user

    data = {'message':''}

    if not user.id == blogger.id and user and blogger:
        return HttpResponseForbidden('Posterboard Only Available for Blogger to Edit')

    if request.method == 'GET' and not request.GET.has_key('_action'):
        return HttpResponseBadRequest()
    # create
    elif request.method == 'POST' and not request.POST.has_key('_action') and element is None:
        # Testing json response:
        #return HttpResponse(json.dumps({'test':1, 'again':2}), mimetype='application/json')

        elementform =  ElementForm(request.POST, prefix='element')
        
        if elementform.is_valid():
            # commit=False creates and returns the model object but doesn't save it.
            # Remove it if unnecessary.
            element = elementform.save(commit=False)
            if element.type !='image' and posterboard.is_user_home_page:
                return HttpResponseForbidden('Only adding images is allowed.')
                
            posterboard.element_set.add(element)

            stateform = StateForm(request.POST, prefix='state')
            if not stateform.is_valid():
                data['errors'] = 'State data isn\'t valid: ' + str(stateform.errors)
                return ErrorResponse(data['errors'], format)
            state = stateform.save(commit=False)
            element.state_set.add(state)

            if element.type == 'image':
                if not 'image' in request.FILES:
                    data['errors'] = 'No Image File is Provided. '
                    return ErrorResponse(data['errors'], format)
                    
                childState = ImageState()
                childState.image=request.FILES['image']
                childState.full_clean()
                state.imagestate = childState

                # Write the element_content, which should be an image
                data['element_content'] = '<img src= "'+childState.image.url+ '"'\
                                            'alt="'+childState.alt+'"'+'>'
                data['element_path'] = childState.image.url
            elif element.type == 'video':
                if not 'video' in request.FILES:
                    data['errors'] = 'No Video File is Provided. '
                    return ErrorResponse(data['errors'], format)
                    
                childState = VideoState()
                childState.original_video=request.FILES['video']
                childState.clean()
                if(childState.original_video.size > settings.MAX_UPLOAD_SIZE):
                    data['errors'] = 'File is too large. ' + \
                                     'Max size allowed is '+ \
                                     str(settings.MAX_UPLOAD_SIZE/1024.0/1024.0) + \
                                     'MB'
                    return ErrorResponse(data['errors'], format)
                state.videostate = childState
            elif element.type == 'audio':
                if not 'audio' in request.FILES:
                    data['errors'] = 'No Audio File is Provided. '
                    return ErrorResponse(data['errors'], format)
                    
                childState = AudioState()
                childState.original_audio=request.FILES['audio']
                #childState.full_clean()
                if(childState.original_audio.size > settings.MAX_UPLOAD_SIZE):
                    data['errors'] = 'File is too large. ' + \
                                     'Max size allowed is '+ \
                                     str(settings.MAX_UPLOAD_SIZE/1024.0/1024.0) + \
                                     'MB'
                    return ErrorResponse(data['errors'], format)
                state.audiostate = childState
            elif element.type == 'text':
                childStateForm = TextStateForm(request.POST, prefix='text')
                if not childStateForm.is_valid():
                    data['errors'] = 'TextState data isn\'t valid: ' + str(childStateForm.errors)
                    return ErrorResponse(data['errors'], format)
                childState = childStateForm.save(commit=False)
                state.textstate = childState
                
                data['element_content'] = childState.content
                
            # TODO: Handle other types of states.
            else: # no matching type
                data['errors'] = 'Element type isn\'t valid: ' + element.type
                return ErrorResponse(data['errors'], format)

            element.save()
            state.save()
            childState.save()
            
            if(element.type == "video"):
                if settings.VIDEO_CONVERT_SYNC:
                    from videologue.management.commands.vlprocess import process_files
                    process_files()
                else: 
                    os.system('python '+ settings.PROJECT_ROOT + '/manage.py vlprocess& 2>&1 1>>'+ settings.LOG_FILENAME)
            
            data['element-id'] = element.id
            data['state-id'] = state.id
            data['child-id'] = childState.pk

            response = render_to_response('elements/wrapper.html', data,
                                          context_instance=RequestContext(request))

            if format == 'html':
                return redirect(posterboard)
            elif format == 'json':
                data['message'] = 'Element created successfully.'
                data['content'] = response.content
                return HttpResponse(json.dumps(data), mimetype='application/json')
        else:
            data['errors'] = 'Element data isn\'t valid: ' + str(elementform.errors)
            logger.debug('Errors creating Element: '+ data['errors'])
            return ErrorResponse(data['errors'], format)

    # Batch update elements
    elif request.method == 'POST' and request.POST.has_key('_action') and request.POST['_action'] == 'put' and \
    blogger.id == user.id:      
        elementForm = ElementForm(request.POST, prefix='element')
        stateForm = StateForm(request.POST, prefix='state')
        
        if elementForm.is_valid() and 'element-id' in request.POST:
            # Retrieve the actual element in the database and update
            actual_element = Element.objects.get(pk=request.POST['element-id'])
            edit_form = ElementForm(request.POST, prefix='element', instance=actual_element)
            edit_form.is_valid() # don't check as we checked above
            edit_form.save()
        else:
            data['message'] += ' Did not update element.'

        if stateForm.is_valid() and 'state-id' in request.POST:
            actual_state = State.objects.get(pk=request.POST['state-id'])
            edit_form = StateForm(request.POST, prefix='state', instance=actual_state)
            edit_form.is_valid()
            edit_form.save()
        else:
            data['message'] += ' Did not update state'

        if 'element-type' in request.POST and 'child-id' in request.POST:
            if request.POST['element-type'] == 'image':
                childStateForm = ImageStateForm(request.POST, prefix='image')
                if not childStateForm.is_valid():
                    data['errors'] = 'Image data isn\'t valid: ' + str(childStateForm.errors)
                    return ErrorResponse(data['errors'], format)
            
                actual_image = ImageState.objects.get(pk=request.POST['child-id'])
                edit_form = ImageStateForm(request.POST, prefix='image', instance=actual_image)
                edit_form.is_valid()
                edit_form.save()
                if 'image' in request.FILES:
                    actual_image.image = request.FILES['image']
            if request.POST['element-type'] == 'video':
                childStateForm = VideoStateForm(request.POST, prefix='video')            
                actual_video = VideoState.objects.get(pk=request.POST['child-id'])
                actual_video.clean()
                edit_form = VideoStateForm(request.POST, prefix='video', instance=actual_video)
                #if not edit_form.is_valid():
                #    data['errors'] = 'Video data isn\'t valid: ' + str(edit_form.errors)
                #    return ErrorResponse(data['errors'], format)
                #edit_form.save()
                if 'video' in request.FILES:
                    actual_video.original_video = request.FILES['video']
            if request.POST['element-type'] == 'audio':
                childStateForm = AudioStateForm(request.POST, prefix='audio')
                actual_audio = AudioState.objects.get(pk=request.POST['child-id'])
                edit_form = AudioStateForm(request.POST, prefix='audio', instance=actual_audio)
                #if not edit_form.is_valid():
                #    data['errors'] = 'Audio data isn\'t valid: ' + str(edit_form.errors)
                #    return ErrorResponse(data['errors'], format)
                #edit_form.save()
                if 'audio' in request.FILES:
                    actual_audio.original_audio = request.FILES['audio']
            elif request.POST['element-type'] == 'text':
                childStateForm = TextStateForm(request.POST, prefix='text')
                if not childStateForm.is_valid():
                    data['errors'] = 'TextState data isn\'t valid: ' + str(childStateForm.errors)
                    return ErrorResponse(data['errors'], format)
                actual_text = TextState.objects.get(pk=request.POST['child-id'])
                edit_form = TextStateForm(request.POST, prefix='text', instance=actual_text)
                edit_form.is_valid()
                edit_form.save()
        else:
            data['message'] += ' Did not update any [type]State'

        if format == 'html':
            return redirect(posterboard)
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # destroy
    elif request.method == 'GET' and request.GET.has_key('_action') and request.GET['_action']=='delete' and \
    element is not None and blogger.id == user.id and element.posterboard_id == posterboard.id:
        data['message'] = 'Successfully removed element '+ str(element.id)
        element.delete()
        
        if format == 'html':
            return redirect(posterboard)
        elif format == 'json':
            return HttpResponse(json.dumps(data), mimetype='application/json')

    # All other types of requests are invalid for this specific scenario.
    error = {'errors': 'Invalid request'}
    return ErrorResponse(error, format)
