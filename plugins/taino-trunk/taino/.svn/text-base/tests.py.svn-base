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

from django.test import TestCase
from taino import demo

class TainoTest(TestCase):
    def test_get_registered_components(self):
        # There are two components with this interface
        self.assertEqual(
            len(demo.IntegerOperation.get_registered_components()),
            2)
        # and only one with this interface
        self.assertEqual(
            len(demo.StringOperation.get_registered_components()),
            1)
        self.assertEqual(
            demo.StringOperation.get_registered_components(),
            [(demo.FirstFiveCharacters.component_id,
              demo.FirstFiveCharacters.component_description)])
        
    def test_get_component_by_id(self):
        add_two_obj = demo.AddTwo()
        self.assertEqual(
            add_two_obj,
            demo.IntegerOperation.get_component_by_id(
                demo.AddTwo.component_id)
            )
        
        self.assertEqual(
            None,
            demo.IntegerOperation.get_component_by_id(
                'this.component.does.not.exist')
            )
    
    def test_singleton(self):
        add_two_obj = demo.AddTwo()
        other_add_two_obj = demo.AddTwo()
        self.assertEqual(add_two_obj, other_add_two_obj)
        
    def test_operation(self):
        i = 26
        i_plus_two = i + 2
        i_doubled = i * 2
        results = demo.IntegerOperation.operate(i)
        self.assert_((demo.AddTwo.component_id, i_plus_two) in results)
        self.assert_((demo.Double.component_id, i_doubled) in results)
    
    def test_lighter_components_float(self):
        expected_result = demo.AddTwo.weight < demo.Double.weight
        operate_data = demo.IntegerOperation.operate(26)
        components_only = map(lambda tpl: tpl[0], operate_data)
        actual_result = components_only.index(demo.AddTwo.component_id) < components_only.index(demo.Double.component_id)
        self.assertEqual(expected_result, actual_result)
        
        # now switch
        tmp = demo.AddTwo.weight
        demo.AddTwo.weight = demo.Double.weight
        demo.Double.weight = tmp
        operate_data = demo.IntegerOperation.operate(26)
        components_only = map(lambda tpl: tpl[0], operate_data)
        actual_result = components_only.index(demo.AddTwo.component_id) < components_only.index(demo.Double.component_id)
        self.assertNotEqual(expected_result, actual_result)
        
        demo.Double.weight = demo.AddTwo.weight
        demo.AddTwo.weight = tmp

            
                
                             
        
