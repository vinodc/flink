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

import os
dir_name = os.path.dirname(__file__)
dir_list = os.listdir(dir_name)
py_files = filter(
    lambda filename: os.path.isfile(os.path.join(dir_name, filename)) and \
        filename.endswith('.py') and filename != '__init__.py',
    dir_list)
__all__ = [os.path.splitext(filename)[0] for filename in py_files]
