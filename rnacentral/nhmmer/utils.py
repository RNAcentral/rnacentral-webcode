"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

import datetime
import requests
import socket

from django.conf import settings
from django.http import HttpResponse

import django_rq
from rq import get_current_job

from nhmmer_search import NhmmerSearch
from nhmmer_parse import NhmmerResultsParser
from models import Results, Query
from settings import EXPIRATION, MAX_RUN_TIME, NHMMER_SERVER


def nhmmer_proxy(request):
    """
    Public-facing nodes forward requests
    to a dedicated machine running nhmmer
    which is not accessible from outside networks.
    """
    if socket.gethostname() not in NHMMER_SERVER:
        nhmmer_url = NHMMER_SERVER + request.get_full_path()
        if request.method == 'POST':
            response = requests.post(nhmmer_url, data=request.POST)
        elif request.method == 'GET':
            response = requests.get(nhmmer_url, params=request.GET)
        return HttpResponse(response.text, status=response.status_code)
    else:
        return None


def save_results(filename, job_id):
    """
    Parse nhmmer results file
    and save the data in the database.
    """
    results = []
    query = Query.objects.get(id=job_id)
    for record in NhmmerResultsParser(filename=filename)():
        record['query_id'] = query
        results.append(Results(**record))
    Results.objects.bulk_create(results, 500)
    query.finished = datetime.datetime.now()
    query.save()


def save_query(sequence, job_id, description):
    """
    Create query object in the main database.
    """
    query = Query(id=job_id,
                  query=sequence,
                  description=description,
                  submitted=datetime.datetime.now())
    query.save()


def nhmmer_search(sequence, description):
    """
    RQ worker function.
    """
    job = get_current_job()
    save_query(sequence, job.id, description)
    filename = NhmmerSearch(sequence=sequence, job_id=job.id)()
    save_results(filename, job.id)


def enqueue_job(query, description):
    """
    Submit job to the queue and return job id.
    """
    queue = django_rq.get_queue()
    job = queue.enqueue_call(func=nhmmer_search,
                             args=(query, description),
                             timeout=MAX_RUN_TIME,
                             result_ttl=EXPIRATION)
    job.meta['query'] = query
    job.meta['expiration'] = datetime.datetime.now() + \
                             datetime.timedelta(seconds=EXPIRATION)
    job.save()
    return job.id


def get_job(job_id):
    """
    Get job from local or remote queues.

    Return a tuple (job, remote_server), where
    * `job` - job object
    * `remote_server` - server where the job was run
                        (None for localhost)
    """
    rq_queues = getattr(settings, 'RQ_QUEUES', [])
    for queue_id, params in rq_queues.iteritems():
        queue = django_rq.get_queue(queue_id)
        job = queue.fetch_job(job_id)
        if job:
            return (job, params['REMOTE_SERVER'])
    return (None, None)
