from django.shortcuts import render_to_response
from django.http import *
from app.models import *
from django.contrib.auth.models import User

from settings import logger

def handle_handlers(func):
    """
    Handle stuff.
    """
    def _dec(*args, **kwargs):
        if kwargs.has_key('format') and kwargs['format'] is None: 
            kwargs['format'] = 'html'
        return func(*args, **kwargs)
    return _dec

def get_blogger(func):
    """
    Get the user whose blog it is based on the username.
    """
    def _dec(*args, **kwargs):
        blogger = kwargs.get('blogger')

        if blogger is not None:
            try:
                blogger = User.objects.get(username=blogger)
            except:
                return HttpResponseBadRequest('Blogger does not exist')

        # Superusers aren't allowed to be bloggers.
        if blogger is not None and blogger.is_superuser:
            return HttpResponseForbidden()
        
        kwargs['blogger'] = blogger
        return func(*args, **kwargs)
    return _dec
    
def get_blogger_settings(func):
    """
    Get the settings object for the giveen blogger
    """
    def _dec(*args, **kwargs):
        blogger = kwargs.get('blogger')
        settings = None
        if blogger is not None:
		# Find the corresponding settings object for blogger
		try:
			settings = blogger.blogsettings
		except:
			settings = BlogSettings(user=blogger)
			settings.save()
                
        kwargs['settings'] = settings
        return func(*args, **kwargs)
    return _dec
        
def get_posterboard(func):
    """
    Get the posterboard that the 'posterboard' refers to.
    """
    def _dec(*args, **kwargs):
        blogger = kwargs.get('blogger')
        pb = kwargs.get('posterboard')

        if blogger is None:
            logger.info("Attempt to access PB without blogger o.O")
            return HttpResponseForbidden('Please specify a blogger first.')

        # Find the PB that corresponds to PB
        if pb is not None:
            try:
                pb = blogger.posterboard_set.get(title_path=pb)
            except:
                return HttpResponseBadRequest('Posterboard Path does not exist')
                
        kwargs['posterboard'] = pb
        return func(*args, **kwargs)
    return _dec

def get_element(func):
    """
    Get the element being referred to.
    """
    def _dec(*args, **kwargs):
        pb = kwargs.get('posterboard')
        element = kwargs.get('element')
        
        if pb is None:
            logger.info("Attempt to access element without PB o.O")
            return HttpResponseForbidden('Please specify a posterboard first.')

        # Find the element being referred to.
        if element is not None:
            try:
                element = int(element)
            except ValueError:
                logger.info('Attempt to access element '+ str(element)+
                            ' for pb '+ str(pb.id))
                return HttpResponseBadRequest('Element should be an id, '+
                                              'which is a number.')
            logger.debug('Trying to find element with id'+ str(element))
            try:
                element = pb.element_set.get(id=element)
            except:
                return HttpResponseBadRequest('Element does not exist')

            logger.debug('Found element!')

        kwargs['element'] = element
        return func(*args, **kwargs)
    return _dec
