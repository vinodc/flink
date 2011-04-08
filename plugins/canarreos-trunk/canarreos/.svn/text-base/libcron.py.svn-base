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


import datetime
import operator
import traceback
import cStringIO
import thread
import syslog
from django.core.mail import mail_admins, mail_managers
from canarreos.api import ICronJob

try:
    import threading
except ImportError:
    pass

syslog.openlog('django', syslog.LOG_CRON)

# Licensing notice:
# Generic python daemon written by Sander Marechal (s.marechal@jejik.com)
# and provided under the Creative Commons CC-BY-SA 3.0 license
# http://creativecommons.org/licenses/by-sa/3.0/
# Some modifications have been made.

import sys, os, time, atexit
import signal

class Daemon(object):
    """
    A generic daemon class.
    
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', 
                 stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.setup()
    
    def setup(self):
        """
        You should implement me.
        """
        pass
    
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        if isinstance(self.stdin, basestring):
            si = open(self.stdin, 'r')
            os.dup2(si.fileno(), sys.stdin.fileno())
        else:
            sys.stdin = self.stdin
        if isinstance(self.stdout, basestring):
            so = open(self.stdout, 'a+')
            os.dup2(so.fileno(), sys.stdout.fileno())
        else:
            sys.stdout = self.stdout
        if isinstance(self.stderr, basestring):
            se = open(self.stderr, 'a+', 0)
            os.dup2(se.fileno(), sys.stderr.fileno())
        else:
            sys.stderr = self.stderr
    
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
        
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.signal(signal.SIGTERM, self.sigterm_handler)
    
    def delpid(self):
        os.remove(self.pidfile)

    def sighup_handler(self):
        syslog.syslog(syslog.INFO, 'SIGHUP received... restarting...')
        self.restart()
    
    def sigterm_handler(self):
        syslog.syslog(syslog.INFO, 'SIGTERM received... stopping...')
        self.stop()

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        # Start the daemon
        syslog.syslog(syslog.LOG_INFO, 'Starting daemon...')
        self.daemonize()
        self.run()
        syslog.syslog(syslog.LOG_INFO, 'Daemon started.')

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            syslog.syslog(syslog.LOG_INFO, 'Stopping daemon...')
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.setup()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. 
        It will be called after the process has been
        daemonized by start() or restart().
        """

# Thus ends the code by Mr. Marechal

def unique(list_of_ints):
    """Given a sorted list of integers, return the sorted list of unique elements."""
    seen = {}
    result = []
    for i in list_of_ints:
        if i in seen: continue
        seen[i] = True
        result.append(i)
    return result

def reduce_cronstring_to_list(cronstyle, max):
    """Reduces a cron-style description of time intervals to a sorted list 
    of integers.
    
    The max argument should indicate the largest numeric value allowed.
    
    * => range(60)
    */20 => [0, 20, 40]
    15,45 => [15, 45]
    1-10,31-40 => [1,2,3,4,5,6,7,8,9,10,31,32,33,34,35,36,37,38,39,40]
    1-10/2 => [2,4,6,8,10]
    """
    max = max - 1
    cronstyle = cronstyle.replace('*','0-%s' % max)
    if ',' in cronstyle:
        # If we have a comma in our string, then we've got multiple ranges
        # so we split it and recurse this function over each
        to_return = reduce(operator.add, 
                           map(lambda s: reduce_cronstring_to_list(s, max+1),
                               cronstyle.split(',')))
    else:
        if '-' in cronstyle:
            if '/' in cronstyle:
                valuerange, divisor = cronstyle.split('/', 1)
            else:
                valuerange, divisor = cronstyle, '1'
            start, end = map(int, valuerange.split('-', 1))
            assert start <= end
            assert end <= max
            assert start >= 0
            to_return = range(start,
                              end+1,
                              int(divisor))
        else:
            assert int(cronstyle) >= 0
            assert int(cronstyle) < max
            to_return = [int(cronstyle)]
    to_return.sort()
    return unique(to_return)

def time_to_run(now, timing):
    """Returns True if the given datetime should run with the given timing."""
    matches_min_hour_day = now.minute in timing['minutes'] and \
        now.hour in timing['hours'] and \
        now.month in timing['months']
    dow_and_day_restricted = timing['days'] != range(31) and \
        timing['dow'] != range(7)
    matches_dow = (now.isoweekday() == 7 and 0 in timing['dow']) or \
          now.isoweekday() in timing['dow']
    matches_day = now.day in timing['days']

    return matches_min_hour_day and \
        ((dow_and_day_restricted and (matches_dow or matches_day)) or \
        (not dow_and_day_restricted and (matches_dow and matches_day)))

class CronDaemon(Daemon):
    def __init__(self, pidfile):
        super(CronDaemon, self).__init__(pidfile, stdin='/dev/null', 
                                         stdout=cStringIO.StringIO(), 
                                         stderr=cStringIO.StringIO())

    def setup(self):
        self.cronjobs = map(lambda tpl: ICronJob.get_component_by_id(tpl[0]),
                            ICronJob.get_registered_components())
        syslog.syslog(syslog.LOG_DEBUG, 'setup: Components found:')
        self.job_timing = {}
        for cronjob in self.cronjobs:
            syslog.syslog(syslog.LOG_DEBUG, 'setup: %s' % cronjob.component_id)
            self.parse_timing(cronjob)

    def parse_timing(self, cronjob):   
        try:
            parts = cronjob.timing().split(' ')
            minute_list = reduce_cronstring_to_list(parts[0], 60)
            hour_list = reduce_cronstring_to_list(parts[1], 24)
            day_list = reduce_cronstring_to_list(parts[2], 31)
            month_list = reduce_cronstring_to_list(parts[3], 12)
            dow_list = reduce_cronstring_to_list(parts[4], 7)
        except Exception, e:
            sys.stderr.write('Error parsing frequency string for %s\n' % \
                cronjob.component_id)
            for line in traceback.format_stack():
                sys.stderr.write(line)
            for line in traceback.format_exception_only(type(e), e):
                sys.stderr.write(line)
            sys.exit(10)
        self.job_timing[cronjob.component_id] = {
            'minutes': minute_list,
            'hours': hour_list,
            'days': day_list,
            'months': month_list,
            'dow': dow_list}
    
    def run(self):
        while 1:
            syslog.syslog(syslog.LOG_DEBUG, 'inner_loop: loop beginning...')
            now = datetime.datetime.now()
            # only run every minute
            time.sleep(60 - now.second)
            now = datetime.datetime.now()
            for job in self.cronjobs:
                syslog.syslog(syslog.LOG_DEBUG, 'Checking %s' % job.component_id)
                # If the timing matches up with now, run.
                timing = self.job_timing[job.component_id]
                syslog.syslog(syslog.LOG_DEBUG, 'Timing is: %s' % timing)
                syslog.syslog(syslog.LOG_DEBUG, 'Now is: %s' % now.timetuple())
                if time_to_run(now, timing):
                    try:
                        syslog.syslog(
                            syslog.LOG_INFO, 'Running %s' % job.component_id)
                        job.run()
                    except Exception, e:
                        # Save the exceptions to stderr
                        sys.stderr.write(
                            'Error while executing cron job for %s :\n' % \
                            job.component_id)
                        for line in traceback.format_stack():
                            sys.stderr.write(line)
                        for line in traceback.format_exception_only(type(e),
                                                                    e):
                            sys.stderr.write(line)
            # Mail stdout to managers and stderr to admins
            if self.stdout.getvalue().strip():
                mail_managers(
                    'Cron output for %s' % now.strftime('%Y-%m-%d %H:%M'),
                    self.stdout.getvalue().strip(),
                    fail_silently=True)
                self.stdout.reset()
                self.stdout.truncate()
            if self.stderr.getvalue().strip():
                mail_admins(
                    'Cron errors for %s' % now.strftime('%Y-%m-%d %H:%M'),
                    self.stderr.getvalue().strip(),
                    fail_silently=True)
                self.stderr.reset()
                self.stderr.truncate()
