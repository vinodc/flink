from django.shortcuts import render_to_response
from django.http import *
from app.models import *

def wrap_in_a(tag):
    """
    Wrap the result of a function in a `tag` HTML tag.
    """
    def _dec(func):
        def _new_func(*args, **kwargs):
            return "<%s>%s</%s>" % (tag, func(*args, **kwargs), tag)
        return _new_func

def get_blogger(func):
    """
    Get the user whose blog it is based on the username.
    """
    def _dec(*args, **kwargs):
        blogger = kwargs.get('blogger')

        if blogger is not None:
            blogger = User.objects.get(username=blogger)

        # Superusers aren't allowed to be bloggers.
        if blogger is not None and blogger.is_superuser:
            return HTTPResponseForbidden()
        
        kwargs['blogger'] = blogger
        return func(*args, **kwargs)
    return _dec


