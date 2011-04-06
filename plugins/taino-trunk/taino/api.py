# -*- coding: utf-8 -*-
"""
Taíno Component System for Django
Copyright (C) 2009, Joshua "jag" Ginsberg <jag@flowtheory.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from django.dispatch import Signal
from django.conf import settings

def __generate_signal_emitter__(cls, new_class, attr):
    return classmethod(lambda cls, *args: new_class.__emit_signal__(attr, *args))


class MetaInterface(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(MetaInterface, cls).__new__(cls, name, bases, attrs)
        # Only execute this for derivatives of Interface
        if name != 'Interface':
            # __registry__ is an singleton instance pool of components that
            # implement this interface
            new_class.__registry__ = {}
            # all of this bootstraps on the django signal system -- each
            # interface gets its own signal
            new_class.__signal__ = Signal(providing_args=['container', 'method', 'nested_args'])
            # voodoo chicken magic to take the declared interface and turn
            # each method into a signal emitter for the registered components
            for attr, value in attrs.items():
                if callable(value) and attr[0] != '_':
                    setattr(new_class, attr, __generate_signal_emitter__(cls, new_class, attr))
        return new_class
    
class Interface(object):
    __metaclass__ = MetaInterface

    @classmethod
    def __emit_signal__(cls, method, *args):
        """A generic signal emitter for registered components"""
        response = []
        results = cls.__signal__.send_robust(cls,
                                             container=response,
                                             method=method,
                                             nested_args=args)
        for receiver, status in results:
            if isinstance(status, type) and issubclass(status, Exception):
                if settings.DEBUG:
                    import pprint
                    pprint.pprint(status.__dict__, stream=sys.stderr)
                raise status
        response.sort(cmp=lambda x, y: cmp(x[1], y[1]))
        return map(lambda tpl: (tpl[0], tpl[2]), response)
    
    @classmethod
    def get_registered_components(cls):
        """Get components registered to this interface with a human readable
        description of that component. Great for choices= definitions."""
        return cls.__emit_signal__('__get_registry__')
    
    @classmethod
    def get_component_by_id(cls, id):
        """Get the singleton instance of a registered component with a specific
        id."""
        return cls.__registry__.get(id, None)        
    
class MetaComponent(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(MetaComponent, cls).__new__(cls, name, bases, attrs)
        if name != 'Component':
            if hasattr(settings, 'DISABLED_COMPONENTS') and \
                cls.component_id in settings.DISABLED_COMPONENTS:
                # simply return the new class
                return new_class
            if not isinstance(new_class.implements, list):
                new_class.implements = [new_class.implements]
            implements = new_class.implements
            singleton = new_class()
            for interface in implements:
                # Connect the component to the interface's signal
                interface.__signal__.connect(receiver=new_class.__handler__, 
                                             sender=interface)
                # Register a singleton instance in the interface's pool
                if new_class.component_id not in interface.__registry__:
                    interface.__registry__[new_class.component_id] = singleton
        return new_class

class Component(object):
    __metaclass__ = MetaComponent
    weight = 100

    def __new__(cls):
        """Singleton factory"""
        new_obj = super(Component, cls).__new__(cls)
        if cls.component_id not in cls.implements[0].__registry__:
            return new_obj
        else:
            return cls.implements[0].__registry__[cls.component_id]

    def __repr__(self):
        return self.component_id

    @classmethod
    def __handler__(cls, container=[], method='', nested_args=[], **kwargs):
        obj = cls()
        method = getattr(obj, method)
        container.append((obj.component_id, obj.weight, method(*nested_args)))
    
    def __get_registry__(self):
        return self.component_description
