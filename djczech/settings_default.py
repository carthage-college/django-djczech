"""
Django settings for project.
"""
#from djzbar.settings import INFORMIX_EARL_PROD as INFORMIX_EARL
from djzbar.settings import INFORMIX_EARL_TEST as INFORMIX_EARL
# sqlserver connection string
MSSQL_EARL = ''
INFORMIX_USERNAME = ''
INFORMIX_PASSWORD = ''
INFORMIX_HOST = ''
INFORMIX_PORT = ''
INFORMIX_DATABASE = ''
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# Debug
DEBUG = False
#DEBUG = True
TEMPLATE_DEBUG = DEBUG
INFORMIX_DEBUG = "debug"
# status codes
IMPORT_STATUS="I"
SUSPICIOUS="s"
AUTO_REC="ar"
REQUI_RICH="r"
REQUI_VICH="v"
if DEBUG:
    SUSPICIOUS="S"
    AUTO_REC="AR"
    REQUI_RICH="R"
    REQUI_VICH="V"
    IMPORT_STATUS="EYE"
# date after which johnson bank cheques are included
# in the check matching view
IMPORT_DATE_FIRST="2015-05-01 00:00:00.0"
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

SECRET_KEY = ''
ALLOWED_HOSTS =  ['localhost','127.0.0.1']
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
SERVER_URL = "www.example.com"
API_URL = "%s/%s" % (SERVER_URL, "api")
LIVEWHALE_API_URL = "https://%s" % (SERVER_URL)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(__file__)
ROOT_URL = "/djczech/"
ROOT_URLCONF = 'djczech.core.urls'
WSGI_APPLICATION = 'djczech.wsgi.application'
MEDIA_ROOT = '{}/assets/'.format(ROOT_DIR)
MEDIA_URL = '/static{}'.format(ROOT_URL)
UPLOADS_DIR = "{}files/".format(MEDIA_ROOT)
CHEQUE_DATA_DIR = "{}cheque-data/".format(UPLOADS_DIR)
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATIC_ROOT = ''
STATIC_URL = "/static/"
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '',
        'NAME': '',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': ''
    },
}
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'djczech',
    'djczech.core',
    'djczech.reconciliation',
    'djtools',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'templates'),
            "/data2/django_templates/djkorra/",
            "/data2/django_templates/djcher/",
            "/data2/django_templates/",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "djtools.context_processors.sitevars",
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.core.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                #'allauth specific context processors',
                #'allauth.account.context_processors.account',
                #'allauth.socialaccount.context_processors.socialaccount',
            ],
            #'loaders': [
            #    # insert your TEMPLATE_LOADERS here
            #]
        },
    },
]
# caching
# LDAP Constants
LDAP_SERVER = ""
LDAP_PORT = ""
LDAP_PROTOCOL = ""
LDAP_BASE = ""
LDAP_USER = ""
LDAP_PASS = ""
LDAP_EMAIL_DOMAIN = ""
LDAP_OBJECT_CLASS = ""
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_ID_ATTR=""
LDAP_AUTH_USER_PK = False
# auth backends
AUTHENTICATION_BACKENDS = ()
LOGIN_URL = '{}accounts/login/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL
USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_DOMAIN=""
SESSION_COOKIE_NAME =''
SESSION_COOKIE_AGE = 60*60
# SMTP settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = True
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL=""
# logging
LOG_FILEPATH = os.path.join(os.path.dirname(__file__), "logs/")
LOG_FILENAME = LOG_FILEPATH + "debug.log"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%Y/%b/%d %H:%M:%S"
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt' : "%Y/%b/%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILENAME,
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'djczech': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'djczech.core': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
