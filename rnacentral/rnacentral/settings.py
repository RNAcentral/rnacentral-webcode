import os

# Django settings for rnacentral project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('RNACENTRAL_SECRET_KEY', '')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # gzip
    'django.middleware.gzip.GZipMiddleware',
    # default
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # django-debug-toolbar
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # django-maintenance
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "portal.context_processors.baseurl",
)

USE_ETAGS=True

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

ROOT_URLCONF = 'rnacentral.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rnacentral.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.humanize',
    'corsheaders',
    'portal',
    'apiv1',
    'rest_framework',
    'debug_toolbar',
    'compressor',
    'markdown_deux',
    'django_rq',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(os.path.realpath(__file__)), "django.log"),
            'maxBytes': 50000, # rollover to the next file
            'backupCount': 1, # keep the previous full log named django.log.1 for backup
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler', # writes to stderr
            'formatter': 'standard'
        },
    },
    'loggers': {
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
        '': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}

# API, django rest framework
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    # API results pagination
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,

    # API throttling
    'DEFAULT_THROTTLE_CLASSES': (
        'apiv1.rest_framework_override.throttling.SafeCacheKeyAnonRateThrottle',
        'apiv1.rest_framework_override.throttling.SafeCacheKeyUserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/second',
        'user': '40/second'
    },

    # Filtering
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),

    # renderers
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        'rest_framework.renderers.YAMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# django-debug-toolbar
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    # 'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    # 'debug_toolbar.panels.signals.SignalDebugPanel',
    # 'debug_toolbar.panels.logger.LoggingPanel',
)

# django-maintenance
MAINTENANCE_MODE = False

# Memcached caching
CACHES = {
  'default': {
    'BACKEND': 'caching.backends.memcached.MemcachedCache', # django-cache-machine
    'LOCATION': 'localhost:11211',
  }
}

# cache queries like Rna.objects.count()
CACHE_COUNT_TIMEOUT = 60 * 60 * 24 # seconds
# by default cache machine doesn't cache empty querysets
CACHE_EMPTY_QUERYSETS = True

# django-markdown-deux
MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
            "fenced-code-blocks": True,
        },
        "safe_mode": False,
    },
}

SILENCED_SYSTEM_CHECKS = ['1_6.W001']

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 8051,
        'DB': 0,
        # 'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': None,
    },
}

try:
   from local_settings import *
except ImportError, e:
   pass
