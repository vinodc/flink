# -*- coding: utf-8 -*-
# Django settings for flink project.

import os.path
import logging

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

#LOG_FILENAME = os.path.join(PROJECT_ROOT, '..', 'logs', 'flink.log')
#logging.basicConfig(
    #format = '%(asctime)s %(levelname)s %(message)s',
    #filename = LOG_FILENAME,
#)

SITE_ID = 1
USE_I18N = True
USE_L10N = True
#MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'static')
#MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
#ADMIN_MEDIA_PREFIX = '/static/admin/'

#debug toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

#caching
CACHE_BACKEND = 'file:///tmp/flink_cache'
GEOTWEET_CACHE_TIME = 24 * 60 * 60      # cache geotweets for a day

#registration
LOGIN_REDIRECT_URL = '/'
ACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = False
SOCIAL_ACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED

ACCOUNT_ACTIVATION_DAYS = 3
#DEFAULT_FROM_EMAIL = 'account@flink.com'
CONTACT_EMAIL = 'support@flink.com'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ayq6rj+cx-*y0+l24_&!&a#v2jo9(p0%wn$l^iow4s@#^$=zg^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

AUTHENTICATION_BACKENDS = (
        'allauth.account.auth_backends.AuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        #'django.core.context_processors.request',
        'allauth.account.context_processors.account', #allauth
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware', #for debugging
]

ROOT_URLCONF = 'flink.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

STATICFILES_DIRS = [
    STATIC_ROOT,
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    #apps
    'flink.apps.core',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.openid',
    'allauth.twitter',
    'allauth.facebook',

    'emailconfirmation',
    'uni_form',
    'oauth2',


    'debug_toolbar',
    'django_extensions',
]
