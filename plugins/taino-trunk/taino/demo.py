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

from taino.api import Component, Interface

class IntegerOperation(Interface):

    def operate(i):
      "Performs some sort of operation on an integer, returning an integer."

class AddTwo(Component):
    implements = IntegerOperation
    component_id = 'net.skwx.taino.AddTwo'
    component_description = 'Add two'
    weight = 10

    def operate(self, i):
        return i+2

class Double(Component):
    implements = IntegerOperation
    component_id = 'net.skwx.taino.Double'
    component_description = 'Double'
    weight = 5

    def operate(self, i):
        return i*2

class StringOperation(Interface):
    def operate(s):
        """Perform some sort of operation on a string, returning a string."""
        

class FirstFiveCharacters(Component):
    implements = StringOperation
    component_id = 'net.skwx.taino.FirstFiveCharacters'
    component_description = 'First five characters'
    
    def operate(self, s):
        return s[:6]
