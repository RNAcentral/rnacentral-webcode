"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=)(PORT=))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=)))',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {
          'threaded': True,
        },
    }
}

TEMPLATE_DIRS = (
	'',
)

STATIC_ROOT = ''

EMAIL_PORT = None # leave None in production, configure in dev if necessary
EMAIL_RNACENTRAL_HELPDESK = ''

SECRET_KEY = ''

ADMINS = (
    ('', ''),
)

COMPRESS_ENABLED = False
DEBUG = False
ALLOWED_HOSTS = []

# django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1',)

# django-maintenance
MAINTENANCE_MODE = False

# Python-rq Redis queues used for exporting results
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 8051,
        'DB': 0,
        # 'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': None,
    },
    'remote': {
        'HOST': '',
        'PORT': 8051,
        'DB': 0,
        # 'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
        'REMOTE_SERVER': '',
    },
}

# destination for the search results files
EXPORT_RESULTS_DIR = os.environ['RNACENTRAL_EXPORT_RESULTS_DIR']
if not os.path.exists(EXPORT_RESULTS_DIR):
    os.makedirs(EXPORT_RESULTS_DIR)
