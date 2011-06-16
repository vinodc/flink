# -*- coding: utf8 -*-
# בש״ד
#
# Canarreos Crontab for Django - Part of the Cuba Libre Project
# Copyright (C) 2009, Joshua "jag" Ginsberg <jag@flowtheory.net>
# 
# Por mi amor, que inspira a mi cada respiración y que echa de Cuba
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from canarreos import libcron

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--pidfile', action='store', type='string', dest='pidfile'),
        )
    
    help = 'Runs a daemon to execute periodically scheduled tasks.'
    args = ''
    
    requires_model_validation = False
    
    def handle(self, *args, **options):
        from taino import models
        pidfile = options.get('pidfile', '')
        if not pidfile:
            raise CommandError('A pidfile is required.')
        pidfile_path, pidfile_name = os.path.split(pidfile)
        pidfile_path = os.path.normpath(pidfile_path)
        if not os.path.exists(pidfile_path):
            raise CommandError(
                '%s does not exist or is not readable' % pidfile_path)
        if not os.access(pidfile_path, os.R_OK|os.W_OK):
            raise CommandError(
                '%s is not writeable for a pidfile' % pidfile_path)
            
        daemon = libcron.CronDaemon(pidfile)
        daemon.start()
        print 'Daemon started.'
