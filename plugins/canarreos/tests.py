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
from django.test import TestCase
from canarreos import libcron

class TestParseCronstring(TestCase):
    
    def test_asterisk(self):
        self.assertEqual(
            libcron.reduce_cronstring_to_list('*', 60),
            range(60))
        self.assertEqual(
            libcron.reduce_cronstring_to_list('*', 30),
            range(30))
    
    def test_atom(self):
        self.assertEqual(libcron.reduce_cronstring_to_list('5', 60), [5])
        self.assertEqual(libcron.reduce_cronstring_to_list('20', 60), [20])
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '61',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '-1',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          'foo',
                          60)
    
    def test_list(self):
        self.assertEqual(libcron.reduce_cronstring_to_list('5,10,15', 60), 
                         [5, 10, 15])
        self.assertEqual(libcron.reduce_cronstring_to_list('2,4,6,8', 60),
                         [2, 4, 6, 8])
        self.assertEqual(libcron.reduce_cronstring_to_list('10,9,8,7', 60),
                         [7, 8, 9, 10])
        self.assertEqual(libcron.reduce_cronstring_to_list('5,5,5,5,5', 60),
                         [5])
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '-1,0,1',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '58,59,60',
                          60)
        
    def test_range(self):
        self.assertEqual(libcron.reduce_cronstring_to_list('1-5', 60),
                         [1, 2, 3, 4, 5])
        self.assertEqual(libcron.reduce_cronstring_to_list('10-20', 60),
                         [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        self.assertEqual(libcron.reduce_cronstring_to_list('5-5', 60), [5])
        self.assertEqual(libcron.reduce_cronstring_to_list('5-6', 60), [5,6])                 
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '20-10',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '-5-5',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '55-65',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          'foo-bar',
                          60)
    
    def test_increment_by(self):
        self.assertEqual(libcron.reduce_cronstring_to_list('*/20', 60),
                         [0, 20, 40])
        self.assertEqual(libcron.reduce_cronstring_to_list('10-20/2', 60),
                         [10, 12, 14, 16, 18, 20])
        self.assertEqual(libcron.reduce_cronstring_to_list('11-19/4', 60),
                         [11, 15, 19])
        self.assertEqual(libcron.reduce_cronstring_to_list('11-20/4', 60),
                         [11, 15, 19])
        self.assertEqual(libcron.reduce_cronstring_to_list('5-5/5', 60),
                         [5])
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '20-10/4',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '-1-1/4',
                          60)
        self.assertRaises(Exception,
                          libcron.reduce_cronstring_to_list,
                          '0-60/5',
                          60)
    
    def test_combinations(self):
        self.assertEqual(libcron.reduce_cronstring_to_list('1-5,20,31-35', 60),
                         [1, 2, 3, 4, 5, 20, 31, 32, 33, 34, 35])
        self.assertEqual(libcron.reduce_cronstring_to_list('*/5,30-35', 60),
                         [0, 5, 10, 15, 20, 25, 30, 31, 32, 33, 34, 35, 40, 45,
                          50, 55])
        self.assertEqual(libcron.reduce_cronstring_to_list('*/10,*/15', 60),
                         [0, 10, 15, 20, 30, 40, 45, 50])
        self.assertEqual(
            libcron.reduce_cronstring_to_list('5-10,20,30-40/2,42,43', 60),
            [5, 6, 7, 8, 9, 10, 20, 30, 32, 34, 36, 38, 40, 42, 43])
 
class TestUnique(TestCase):
    def test_unique(self):
        self.assertEqual(libcron.unique([5,5,5,5,5]),
                                        [5])
        self.assertEqual(libcron.unique([1,1,2,2,3,3,4,4,5,5]),
                                        [1,2,3,4,5])
        self.assertEqual(libcron.unique([1,2,3,4,5]),
                                        [1,2,3,4,5])
        self.assertEqual(libcron.unique([1,2,3,3,4,5]),
                                        [1,2,3,4,5])

class TestTimeToRun(TestCase):
    all_stars = {'minutes': range(60),
                 'hours': range(24),
                 'days': range(31),
                 'months': range(12),
                 'dow': range(7)}
    
    def test_allstars(self):
        now = datetime.datetime.now()
        self.assert_(libcron.time_to_run(now, self.all_stars))
    
    def test_minutes(self):
        now = datetime.datetime.now()
        timing = self.all_stars.copy()
        timing['minutes'] = [now.minute]
        self.assert_(libcron.time_to_run(now, timing))
        
        now += datetime.timedelta(seconds=60)
        self.assertNotEqual(now.minute, timing['minutes'][0])
        self.assertFalse(libcron.time_to_run(now, timing))
    
    def test_hours(self):
        now = datetime.datetime.now()
        timing = self.all_stars.copy()
        timing['hours'] = [now.hour]
        self.assert_(libcron.time_to_run(now, timing))
        
        now += datetime.timedelta(minutes=60)
        self.assertNotEqual(now.hour, timing['hours'][0])
        self.assertFalse(libcron.time_to_run(now, timing))

    def test_months(self):
        now = datetime.datetime.now()
        timing = self.all_stars.copy()
        timing['months'] = [now.month]
        self.assert_(libcron.time_to_run(now, timing))
        
        now += datetime.timedelta(days=31)
        self.assertNotEqual(now.month, timing['months'][0])
        self.assertFalse(libcron.time_to_run(now, timing))
    
    def test_days_and_dow(self):
        # test all stars and day match
        now = datetime.datetime.now()
        timing = self.all_stars.copy()
        timing['days'] = [now.day]
        self.assert_(libcron.time_to_run(now, timing))
        
        # test all stars and dow match
        timing['days'] = self.all_stars['days']
        timing['dow'] = [now.isoweekday()]
        self.assert_(libcron.time_to_run(now, timing))
        
        # even if day doesn't match, if dow does, it should run
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        timing['days'] = [tomorrow.day]
        self.assert_(libcron.time_to_run(now, timing))
        
        # even if dow doesn't match, if day does, it should run
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        timing['dow'] = [tomorrow.isoweekday()]
        timing['days'] = [now.day]
        self.assert_(libcron.time_to_run(now, timing))
        
        # if only one of he two is restricted and it doesn't match, it should
        # not run
        timing['days'] = [tomorrow.day]
        timing['dow'] = self.all_stars['dow']
        self.assertFalse(libcron.time_to_run(now, timing))
        timing['days'] = self.all_stars['days']
        timing['dow'] = [tomorrow.isoweekday()]
        self.assertFalse(libcron.time_to_run(now, timing))
        
        # also make sure 0 == 7 for dow
        now = datetime.datetime(2009, 9, 6, 12, 0, 0)
        timing = self.all_stars.copy()
        timing['dow'] = [0]
        self.assertEqual(now.isoweekday(), 7)
        self.assert_(libcron.time_to_run(now, timing))
        
        

        