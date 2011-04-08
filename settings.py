# -*- coding: utf-8 -*-
# Django settings for flink project.

import os.path
import logging

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

AUTH_PROFILE_MODULE = 'app.Profile'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sqlite3.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MEDIA_SERVER = {
    'PROTOCOL': 'http',
    'HOST': '127.0.0.1',
    'PORT':  8086,
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LOG_FILENAME = os.path.join(PROJECT_ROOT, 'logs', 'flink.log')
logging.basicConfig(
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILENAME,
)
logger = logging.getLogger()


SITE_ID = 1

# Video
VIDEOLOGUE_ENCODE_FLV = False
VIDEOLOGUE_ENCODE_OGV = True
VIDEOLOGUE_ENCODE_MP4 = False
VIDEOLOGUE_VIDEO_SIZE = '720x480'
VIDEOLOGUE_IMAGE_SIZE = '720x480'
VIDEO_CONVERT_SYNC = False # Don't set this to True, unless you are testing. This is handled in test.
PHOTOLOGUE_DIR = 'videos'
VIDEOLOGUE_DIR = 'videos' 
CONVERSION_TIME = 55 # in seconds
MAX_UPLOAD_SIZE = 50.0*1024*1024 # 50MB in bytes

# Cron
# django_cron
CRON_POLLING_FREQUENCY = 45

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
TEST_MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test-media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = os.path.join(PROJECT_ROOT, 'raw-static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative
    os.path.join(PROJECT_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#debug toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

#caching
CACHE_BACKEND = 'file:///tmp/flink_cache'

#registration
LOGIN_REDIRECT_URL = '/'
ACCOUNT_NAME_REQUIRED = True #requires first and last name
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = False  #keeps account inactive until email is verified
ACCOUNT_EMAIL_AUTHENTICATION = True #uses email+pass instead of username+pass
ACCOUNT_USERNAME_REQUIRED = True    #generates a random username
ACCOUNT_PASSWORD_VERIFICATION = True #requires password to be entered twice
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED #use 3rd parties for email
SOCIALACCOUNT_AUTO_SIGNUP = False
EMAIL_CONFIRMATION_DAYS = 3
DEFAULT_FROM_EMAIL = 'signup@flink.com'
CONTACT_EMAIL = 'support@flink.com'

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

#PERSISTENT_SESSION_KEY = 'sessionpersistent'
#SESSION_COOKIE_AGE = 120960

TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        #'django.core.context_processors.request',
        'allauth.account.context_processors.account', #allauth
)

MIDDLEWARE_CLASSES = (
    #'account.middleware.DualSessionMiddleware', # django-account
    #'account.middleware.AccountBasedAuthentication', # django-account
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware', #for debugging
)

ROOT_URLCONF = 'flink.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'account',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     # Uncomment next two lines to enable admin and admindocs:
    'django.contrib.admin',
    'django.contrib.admindocs',

    # apps
    'flink.app',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.openid',
    'allauth.twitter',
    'allauth.facebook',

    'emailconfirmation',
    'uni_form',
    'oauth2',

    # video
    'photologue',
    'videologue',
    'batchadmin',
    'cpserver',
    
    # cron
    #'plugins',
    #'taino',
    #'canarreos',
    #'django_cron',
    
    'debug_toolbar',
    'django_extensions',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}
