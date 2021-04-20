"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

from dotenv import load_dotenv

DEBUG = os.getenv('DJANGO_DEBUG', False)

# project root directory
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # pylint: disable=C0301

# read environment variables
load_dotenv(os.path.join(PROJECT_PATH, '.env'))

ADMINS = (
    ('RNAcentral Team', ''.join(['rnacentral', '@', 'gmail.com'])),
)

MANAGERS = ADMINS

# use the public Postgres database as the default value
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'pfmegrnargs'),
        'USER': os.getenv('DB_USERNAME', 'reader'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'NWDMCE5xdipIjRrp'),
        'HOST': os.getenv('DB_HOST', 'hh-pgsql-public.ebi.ac.uk'),
        'PORT': os.getenv('DB_PORT', 5432),
    }
}
CONN_MAX_AGE = 300

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

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

# We cache sitemaps as static files into a specific folder on hard drive
SITEMAPS_ROOT = os.path.join(PROJECT_PATH, 'rnacentral', 'sitemaps')
# We use empty prefix for sitemaps, cause they should cover the whole site
SITEMAPS_URL = '/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_PATH), 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# WhiteNoise - compression and caching support
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
    'compressor.finders.CompressorFinder',
)

# Provide an initial value so that the site is functional with default settings
SECRET_KEY = os.getenv('SECRET_KEY', 'use environment variable or override this in local_settings.py')

MIDDLEWARE = (
    # WhiteNoise - serve static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',  # django or jinja
    'DIRS': (
        os.path.join(PROJECT_PATH, 'rnacentral', 'templates'),
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
    ),
    # 'APP_DIRS': True,  # look for templates in app subdirectories
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.debug",
            "django.template.context_processors.i18n",
            "django.template.context_processors.media",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            "django.contrib.messages.context_processors.messages",
            "django.template.context_processors.request",
            "portal.context_processors.baseurl",
        ],
        'loaders': [
            # List of callables that know how to import templates from various sources.
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
        'debug': DEBUG
    }
}]

USE_ETAGS = True

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'rnacentral.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rnacentral.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'corsheaders',
    'portal',
    'sequence_search',
    'apiv1',
    'django_filters',  # required by DRF3.5+
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
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",  # pylint: disable=W0401, C0301
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'rq_console': {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',  # writes to stderr
            'formatter': 'standard'
        },
        'rq_console': {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.server': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'rq.worker': {
            "handlers": ["rq_console"],
            "level": "DEBUG"
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
    'DEFAULT_PAGINATION_CLASS': 'rnacentral.utils.pagination.Pagination',
    'PAGE_SIZE': 10,
    # 'PAGINATE_BY_PARAM': 'page_size', - this parameter no longer works - we had to subclass pagination class instead
    'MAX_PAGINATE_BY': 1000000000000,

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
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

    # renderers
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_jsonp.renderers.JSONPRenderer',
        'rest_framework_yaml.renderers.YAMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# django-debug-toolbar
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# django-maintenance
MAINTENANCE_MODE = False

# Memcached caching for django-cache-machine
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:8052',
    },
    'sitemaps': {
        'BACKEND': 'rnacentral.utils.cache.SitemapsCache',
        'LOCATION': SITEMAPS_ROOT
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
            "tables": None,
            "fenced-code-blocks": True,
        },
        "safe_mode": False,
    },
}

SILENCED_SYSTEM_CHECKS = ['1_6.W001']

EBI_SEARCH_ENDPOINT = 'http://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral'

RELEASE_ANNOUNCEMENT_URL = 'https://blog.rnacentral.org/2021/03/rnacentral-release-17.html'

# django compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]


# Use a simplified runner to prevent any modifications to the database.
TEST_RUNNER = 'portal.tests.runner.FixedRunner'

from .local_settings import *  # pylint: disable=W0401, W0614
