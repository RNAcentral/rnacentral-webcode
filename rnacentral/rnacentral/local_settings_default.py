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

from utils import get_environment

SECRET_KEY = ''

ORACLE_DBS = {
    'HX': {
        'host': '',
        'port': 0,
        'user': '',
        'service': '',
    },
    'OY': {
        'host': '',
        'port': 0,
        'user': '',
        'service': '',
    },
    'PG': {
        'host': '',
        'port': 0,
        'user': '',
        'service': '',
    },
    'DEV': {
        'host': '',
        'port': 0,
        'user': '',
        'service': '',
    },
}

ENVIRONMENT = get_environment()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': ('(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})'
                 '(PORT={port}))(CONNECT_DATA=(SERVER=DEDICATED)'
                 '(SERVICE_NAME={service})))').format(
                     host=ORACLE_DBS[ENVIRONMENT]['host'],
                     port=ORACLE_DBS[ENVIRONMENT]['port'],
                     service=ORACLE_DBS[ENVIRONMENT]['service'],
                     ),
        'USER': ORACLE_DBS[ENVIRONMENT]['user'],
        'PASSWORD': '',
        'OPTIONS': {
            'threaded': True,
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

DEBUG = True
COMPRESS_ENABLED = False

# django-debug-toolbar
# print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR']) in views
INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')
