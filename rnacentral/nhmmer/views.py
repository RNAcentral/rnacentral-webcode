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
import django_rq

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from rq import get_current_job

from nhmmer.settings import MIN_LENGTH, MAX_LENGTH, EXPIRATION, MAX_RUN_TIME
from nhmmer.messages import messages
from nhmmer.nhmmer_search import NhmmerSearch


def nhmmer_search(sequence):
    """
    RQ worker function.
    """
    job = get_current_job()
    return NhmmerSearch(sequence=sequence, job_id=job.id)()

    # parse results and store in db


def enqueue_job(query):
    """
    Submit job to the queue and return job id.
    """
    queue = django_rq.get_queue()
    job = queue.enqueue_call(func=nhmmer_search,
                             args=(query,),
                             timeout=MAX_RUN_TIME,
                             result_ttl=EXPIRATION)
    job.meta['query'] = query
    job.meta['expiration'] = datetime.datetime.now() + \
                             datetime.timedelta(seconds=EXPIRATION)
    job.save()
    return job.id


@never_cache
@csrf_exempt # to enable POST requests
def submit_job(request):
    """
    Start nhmmer search.

    HTTP responses:
    * 201 - job submitted
    * 400 - incorrect input
    * 500 - internal error
    """
    msg = messages['submit']

    if request.method == 'POST':
        query = request.POST.get('q', '')
    elif request.method == 'GET':
        query = request.GET.get('q', '')

    if not query:
        status = 400
        return JsonResponse(msg[status]['no_sequence'], status=status)

    if len(query) < MIN_LENGTH:
        status = 400
        return JsonResponse(msg[status]['too_short'], status=status)
    elif len(query) > MAX_LENGTH:
        status = 400
        return JsonResponse(msg[status]['too_long'], status=status)

    try:
        status = 201
        job_id = enqueue_job(query)
        return JsonResponse({'job_id': job_id}, status=status)
    except:
        status = 500
        return JsonResponse(msg[status], status=status)

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

@never_cache
def get_status(request):
    """
    Get status of an nhmmer search.

    HTTP responses:
    * 200 - job found
    * 400 - job id not provided in the url
    * 404 - job not found in the queue
    * 500 - internal error
    """
    msg = messages['status']

    job_id = request.GET.get('job', '')
    if not job_id:
        status = 400
        return JsonResponse(msg[status], status=status)

    try:
        job = get_job(job_id)[0]
        if job:
            data = {
                'id': job.id,
                'status': job.get_status(),
                'enqueued_at': str(job.enqueued_at),
                'ended_at': str(job.ended_at),
                'expiration': job.meta['expiration'].strftime("%m/%d/%Y"),
            }
            return JsonResponse(data)
        else:
            status = 404
            return JsonResponse(msg[status], status=status)
    except:
        status = 500
        return JsonResponse(msg[status], status=status)
