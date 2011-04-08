# -*- coding: utf-8 -*-
import os
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR, 'videologue')

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
#http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Dynamically calculate the version based on videologue.VERSION
version_tuple = __import__('videologue').VERSION
if len(version_tuple) == 3:
    version = "%d.%d_%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

# Scan for and add any data files    
data_files = []

for dirpath, dirnames, filenames in os.walk(SOURCE_DIR):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        dirpath = dirpath.replace(ROOT_DIR, '').strip(os.path.sep)
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "videologue",
    version = version,
    description = "Powerful video management for the Django web framework.",
    author = "Øyvind Saltvik",
    author_email = "oyvind.saltvikl@gmail.com",
    url = "http://github.com/fivethreeo/django-videologue/tree/master",
    packages = ['videologue',
                'videologue.management',
                'videologue.management.commands',
                'videologue.templatetags'],
    data_files = data_files,
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
