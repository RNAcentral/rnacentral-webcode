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

import importlib
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from django_rq.queues import get_queues

from redis.exceptions import ConnectionError
from rq import use_connection
from rq.utils import ColorizingStreamHandler

from nhmmer.utils import error_handler


# Setup logging for RQWorker if not already configured
logger = logging.getLogger('rq.worker')
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                                  datefmt='%H:%M:%S')
    handler = ColorizingStreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Copied from rq.utils
def import_attribute(name):
    """Return an attribute from a dotted path name (e.g. "path.to.func")."""
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


class Command(BaseCommand):
    """
    Runs RQ workers on specified queues. Note that all queues passed into a
    single rqworker command must share the same connection.

    Example usage:
    python manage.py nhmmer_worker high medium low
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--burst',
            action='store_true',
            dest='burst',
            default=False,
            help='Run worker in burst mode'
        ),
        make_option(
            '--worker-class',
            action='store',
            dest='worker_class',
            default='rq.Worker',
            help='RQ Worker class to use'
        ),
        make_option(
            '--name',
            action='store',
            dest='name',
            default=None,
            help='Name of the worker'
        ),
    )
    args = '<queue queue ...>'

    def handle(self, *args, **options):
        try:
            # Instantiate a worker
            worker_class = import_attribute(options.get('worker_class', 'rq.Worker'))
            queues = get_queues(*args)
            w = worker_class(queues, connection=queues[0].connection, name=options['name'])

            # add custom nhmmer error handler
            w.push_exc_handler(error_handler)

            # Call use_connection to push the redis connection into LocalStack
            # without this, jobs using RQ's get_current_job() will fail
            use_connection(w.connection)
            w.work(burst=options.get('burst', False))
        except ConnectionError as e:
            print(e)
