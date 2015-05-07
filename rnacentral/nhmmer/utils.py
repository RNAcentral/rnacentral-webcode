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
import os
import re
import requests
import signal
import socket
import subprocess
import traceback

from django.conf import settings
from django.core.mail import send_mail
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
                  query=sequence.upper(),
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
    queue = django_rq.get_queue('nhmmer')
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


def kill_nhmmer_job(job_id):
    """
    Get pid of an nhmmer job based on its id and kill it.
    """
    pid = None
    job_killed = None

    cmd = 'ps -eo pid,args | grep nhmmer' # print process id and full command
    output = subprocess.check_output(cmd, shell=True)
    for line in output.split('\n'):
        if job_id in line:
            match = re.match(r'^(\d+)\s+', line)
            if match:
                pid = int(match.group(1))
    if pid:
        try:
            os.kill(pid, signal.SIGQUIT) # quit from keyboard
            job_killed = True
        except:
            job_killed = False
    return job_killed


def error_handler(job, exc_type, exc_value, exc_traceback):
    """
    If a job times out or in case of other exceptions
    kill nhmmer process (if it still exists)
    and send an email notification to the Admins.
    """
    try:
        # job was cancelled, don't send a notification
        if abs(exc_value[2]) == signal.SIGQUIT:
            return
    except:
        pass
    # kill job
    job_killed = kill_nhmmer_job(job.id)
    # format traceback
    traceback_formatted = '\n'.join(traceback.format_exception(exc_type,
        exc_value, exc_traceback))
    # compose and send email alert
    subject = 'Nhmmer error'
    message = (
        'Traceback:\n'
        '{0}\n'
        'Job id: {1}\n'
        'job_killed: {2}\n'
    ).format(traceback_formatted, job.id, job_killed)
    for (_, email) in settings.ADMINS:
        _from = email
        send_mail(subject, message, _from, [email])
