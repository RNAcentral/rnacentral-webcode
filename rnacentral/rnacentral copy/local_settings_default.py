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

from utils import get_environment


DEBUG = True
COMPRESS_ENABLED = False

SECRET_KEY = ''

DBS = {
    'HX': {
        'user': '',
        'name': '',
    },
    'OY': {
        'user': '',
        'name': '',
    },
    'PG': {
        'user': '',
        'name': '',
    },
    'DEV': {
        'user': '',
        'name': '',
        'host': '',
        'port': 5432,
    },
}

ENVIRONMENT = get_environment()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2,',
        'NAME': DBS[ENVIRONMENT]['name'],
        'USER': DBS[ENVIRONMENT]['user'],
        'PASSWORD': '',
        'HOST': DBS[ENVIRONMENT]['host'],
        'port': DBS[ENVIRONMENT]['port'],
        'OPTIONS': {
        }
    },
    'nhmmer_db': {
        'NAME': 'nhmmer_results',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': 0,
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 8051,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': None,
    },
}

# Python-rq Redis queues used for exporting results
if ENVIRONMENT == 'OY':
    RQ_QUEUES['remote'] = {
        'HOST': 'ves-pg-XX.ebi.ac.uk',
        'PORT': 8051,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': 'ves-pg-XX.ebi.ac.uk:8050',
    }
elif ENVIRONMENT == 'PG':
    RQ_QUEUES['remote'] = {
        'HOST': 'ves-oy-XX.ebi.ac.uk',
        'PORT': 8051,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': 'ves-oy-XX.ebi.ac.uk:8050',
    }

# django-debug-toolbar
# print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR']) in views
INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')

# Note that this is basically the same as the standard settings tuple, but with
# the addition of the django_performance_testing app. This app is required so
# that the performance tests will pass.
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
    'nhmmer',
    'apiv1',
    'rest_framework',
    'debug_toolbar',
    'compressor',
    'markdown_deux',
    'django_rq',
    'django_performance_testing',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)
