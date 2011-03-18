from django.shortcuts import render_to_response
from django.http import *
from app.models import *
from django.contrib.auth.models import User

from settings import logger


def test_concurrently(times):
    """ 
    Add this decorator to small pieces of code that you want to test
    concurrently to make sure they don't raise exceptions when run at the
    same time.  E.g., some Django views that do a SELECT and then a subsequent
    INSERT might fail when the INSERT assumes that the data has not changed
    since the SELECT.
    """
    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []
            import threading
            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception, e:
                    exceptions.append(e)
                    raise
            threads = []
            for i in range(times):
                threads.append(threading.Thread())
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception('test_concurrently intercepted %s exceptions: %s' % (len(exceptions), exceptions))
        return wrapper
    return test_concurrently_decorator


def wrap_in_a(tag):
    """
    Wrap the result of a function in a `tag` HTML tag.
    """
    def _dec(func):
        def _new_func(*args, **kwargs):
            return "<%s>%s</%s>" % (tag, func(*args, **kwargs), tag)
        return _new_func

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

def get_set(func):
    """
    Get the posterboard that the 'posterboard' refers to.
    """
    def _dec(*args, **kwargs):
        blogger = kwargs.get('blogger')
        pbset = kwargs.get('set')

        if blogger is None:
            logger.info("Attempt to access PB set without blogger o.O")
            return HttpResponseForbidden('Please specify a blogger first.')
        
        try:
            pbset = int(pbset)
        except ValueError:
            logger.info('Attempt to access PB set' + str(pbset))
            return HttpResponseBadRequest('Set should be an id, '+
                                          'which is a number.')

        kwargs['set'] = pbset
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
