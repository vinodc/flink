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
import pprint
from django.db import models
from django.conf import settings

class ComponentField(models.Field):
    __metaclass__ = models.SubfieldBase 
    
    # empty_strings_allowed = False
    def __init__(self, verbose_name=None, name=None, interface=None, **kwargs):
        self.interface = interface
        kwargs['choices'] = interface.get_registered_components()
        kwargs['max_length'] = 250
        models.Field.__init__(self, verbose_name, name, **kwargs)
    
    def get_internal_type(self):
        return "CharField"
    
    def to_python(self, value):
        if hasattr(value, 'component_id'):
            return value
        else:
            return self.interface.get_component_by_id(value)

    def get_db_prep_value(self, value):
        # print 'get_db_prep_value', value
        return self.value_to_string(value)

    def value_to_string(self, obj):
        # print 'value_to_string', obj
        if obj:
            return obj.component_id
        else:
            return ''

# Automatically load any code in plugins/ directories for all installed apps
#
# If there are any models in the plugins, register those models with their
# appropriate app.
loaded = False
apps = models.get_apps()
if not loaded:
    for app in apps:
        app_name = '.'.join(app.__name__.split('.')[:-1])
        if settings.DEBUG:
            sys.stderr.write('Looking for plugins in %s\n' % app_name)
        app_mod = __import__(app_name, {}, {}, ['plugins'])
        if hasattr(app_mod, 'plugins'):
            if settings.DEBUG:
                sys.stderr.write('Loading plugins for %s\n' % app_mod)
            plugins = __import__(app_name+'.plugins', {}, {}, ['*'])
            plugin_mods = map(lambda plugin: getattr(plugins, plugin),
                              plugins.__all__)
            for plugin_mod in plugin_mods:
                model_objs = filter(
                    lambda attr: isinstance(attr, type) and issubclass(attr, models.Model),
                    plugin_mod.__dict__.values()
                )
                for model_obj in model_objs:
                    if model_obj._meta.app_label == 'plugins':
                        model_obj._meta.app_label = app_name.split('.')[-1]
                        model_obj._meta.db_table = '%s_%s' % \
                            (app_name.split('.')[-1],
                             model_obj._meta.module_name)
                        models.loading.cache.register_models(app_name.split('.')[-1],
                                                             *model_objs)
    loaded = True


