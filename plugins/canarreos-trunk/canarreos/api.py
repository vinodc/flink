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

from taino.api import Interface

class ICronJob(Interface):
    
    def timing():
        """Returns a crontab like time definition for what time this job should
        run.
        
        Examples:
        
        '*/5 * * * *' -- Run every 5 minutes
        '0 * * * 1-5' -- Run on the hour every weekday
        '0 4 1 * *' -- Run at 4am on the first day of each month
        '0-20/4,35-40,50-59/2 * 15 1,2,5,7 0' -- Run every 4th minute from the 0th
        to the 20th minute, every minute from the 35th to the 40th, and every
        other minute from the 50th to the 59th every hour of every day in a 
        month ending in "y" that is a Sunday or the 15th of the month
        """

    def run():
        """Returns nothing. Does whatever you want. Any output to stdout will
        be send to managers. Any output to stderr or any exceptions will be
        send to admins."""

