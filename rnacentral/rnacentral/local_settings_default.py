
import os
from utils import get_environment

if get_environment() == 'DEV':
    DEBUG = True

SECRET_KEY = ''

ENVIRONMENT = get_environment()

from .databases import DATABASES
from .rq_queues import RQ_QUEUES
from .ebi_search_endpoints import EBI_SEARCH_ENDPOINT
from .compressor import *

# print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR']) in views
INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')

# databases settings
DATABASES['nhmmer_db'] = {
    'NAME': '',
    'ENGINE': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': 3306
}
