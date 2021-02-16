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
from __future__ import print_function
import six

import datetime
import django_rq
import gzip
import json
import logging
import os
import requests
import subprocess as sub
import tempfile

from django.conf import settings
from wsgiref.util import FileWrapper
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.text import get_valid_filename
from django.views.decorators.cache import never_cache

from contextlib import closing
from rq import get_current_job
from rest_framework import renderers
from rest_framework.test import APIRequestFactory

from apiv1.serializers import RnaPrecomputedJsonSerializer
from portal.models import RnaPrecomputed
from .settings import EXPIRATION, MAX_RUN_TIME, ESLSFETCH, FASTA_DB, MAX_OUTPUT,\
                     EXPORT_RESULTS_DIR


def export_search_results(query, _format, hits):
    """
    RQ worker function.

    * paginate over EBI search results results
    * extract RNAcentral ids
    * write the data to a local file in the specified format
    * return the filename
    """
    def get_results_page(start, end):
        """
        Retrieve a page of search results and return RNAcentral ids.
        """
        page_size = end - start
        url = ''.join([settings.EBI_SEARCH_ENDPOINT,
                       '?query={query}',
                       '&start={start}',
                       '&size={page_size}',
                       '&format=json']).format(query=query, start=start, page_size=page_size)
        data = json.loads(requests.get(url).text)
        return [entry['id'] for entry in data['entries']]

    def format_output(rnacentral_ids):
        """
        Given a list of RNAcentral ids, return the results.
        """
        # filter queryset to hold only specific rnacentral ids
        queryset = RnaPrecomputed.objects.filter(id__in=rnacentral_ids).iterator()
        factory = APIRequestFactory()
        fake_request = factory.get('/')
        serializer_context = {'request': fake_request}
        serializer = RnaPrecomputedJsonSerializer(queryset, context=serializer_context, many=True)

        renderer = renderers.JSONRenderer()
        output = renderer.render(serializer.data)
        # omit opening and closing square brackets for easy concatenation
        output = output[1:-1]
        # make relative urls absolute
        # output = output.replace('"/api/v1/', '"https://rnacentral.org/api/v1/')
        return output

    def check_ssi_file():
        """
        Easel esl-sfetch can index the FASTA database for faster performance.
        If SSI index does not exist, create it.
        """
        ssi_index = FASTA_DB + '.ssi'
        if os.path.exists(ssi_index):
            return
        cmd = '{esl_binary} --index {fasta_db}'.format(
            esl_binary=ESLSFETCH,
            fasta_db=FASTA_DB
        )
        process = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = process.communicate()
        return_code = process.returncode
        if return_code != 0:
            class EaselIndexError(Exception):
                """Raise when Easel could not index the fasta database"""
                pass
            raise EaselIndexError(errors, output + b'\n' + cmd.encode(), return_code)

    def run_easel(temp_file, filename):
        """
        Export RNAcentral ids saved in a temporary file using Easel esl-sfetch
        for accessing the FASTA database.
        """
        # check that SSI index exists, create if necessary
        check_ssi_file()
        # make sure that temporary file is saved to disk
        temp_file.flush()
        os.fsync(temp_file.fileno())
        cmd = '{esl_binary} -f {fasta_db} {id_list} | gzip > {output}'.format(
            esl_binary=ESLSFETCH,
            fasta_db=FASTA_DB,
            id_list=temp_file.name,
            output=filename)
        process = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = process.communicate()
        return_code = process.returncode
        temp_file.close()
        if return_code != 0:
            class EaselError(Exception):
                """Raise when Easel exits with a non-zero status"""
                pass
            raise EaselError(errors, output + b'\n' + cmd.encode(), return_code)

    def paginate_over_results():
        """
        Paginate over the results and write out the data to an archive.
        JSON requires special treatment in order to concatenate
        multiple batches
        """
        filename = os.path.join(EXPORT_RESULTS_DIR,
                                '%s.%s.gz' % (job.id, _format))
        start = 0
        page_size = 100  # max EBI search page size

        if _format in ['json', 'list']:
            archive = gzip.open(filename, 'wb')
        if _format == 'json':
            archive.write(b'[')
        if _format == 'fasta':
            f = tempfile.NamedTemporaryFile(delete=True, dir=EXPORT_RESULTS_DIR)

        while start < hits:
            max_end = start + page_size
            end = min(max_end, hits)
            rnacentral_ids = get_results_page(start, end)
            if _format == 'fasta':
                # write out RNAcentral ids to a temporary file
                for _id in rnacentral_ids:
                    line = str.encode(_id+'\n')
                    f.write(line)
            if _format == 'list':
                text = str.encode('\n'.join(rnacentral_ids) + '\n')
                archive.write(text)
            if _format == 'json':
                text = format_output(rnacentral_ids)
                archive.write(text)
                # join batches with commas except for the last iteration
                if text and end != hits:
                    archive.write(b',\n')
            start = end

            job.meta['progress'] = min(round(float(start) * 100 / hits, 2), 85)
            # job.save_meta()
            job.save()

        if _format == 'json':
            archive.write(b']')
            archive.close()
        if _format == 'fasta':
            run_easel(f, filename)

        job.meta['progress'] = 100
        # job.save_meta()
        job.save()
        return filename

    job = get_current_job()
    job.refresh()
    filename = paginate_over_results()
    return filename


def get_job(job_id):
    """
    Get job from local or remote queues.

    Return a tuple (job, remote_server), where
    * `job` - job object
    * `remote_server` - server where the job was run
                        (None for localhost)
    """
    rq_queues = getattr(settings, 'RQ_QUEUES', [])
    for queue_id, params in six.iteritems(rq_queues):
        queue = django_rq.get_queue(queue_id)
        job = queue.fetch_job(job_id)
        if job:
            return (job, params['REMOTE_SERVER'])
    return (None, None)


@never_cache
def download_search_result_file(request):
    """
    Internal API.
    Download a file with metadata search results given a job id.
    To control memory usage the file is returned in small chunks via Django.

    HTTP responses:
    * 400 - job id not provided in the url
    * 404 - job id not found in the queue
    * 500 - internal error
    * 202 - result is not ready yet
    """
    def get_download_filename():
        """
        Construct a descriptive name for the downloadable file.
        Use a standard Django function for making valid filenames.
        """
        max_length = 200
        query = job.meta['query']
        extension = os.path.splitext(job.result)[1]
        if len(query) > max_length:
            name = query[:max_length] + '_etc'
        else:
            name = query
        filename = name + '.' + job.meta['format'] + extension
        return get_valid_filename(filename)

    def get_content_type():
        """
        Set content type based on the export format.
        """
        content_types = {
            'fasta': 'text/fasta',
            'json': 'application/json',
            'list': 'text/plain',
            'default': 'text/plain',
        }
        _format = job.meta['format']
        if _format in content_types:
            return content_types[_format]
        else:
            return content_types['default']

    def stream_remote_file(server):
        """
        Connect to remote server where the job is found,
        retrieve the results file and pass it through to the user.
        """
        url = ''.join(['http://', server, request.get_full_path()])
        with closing(requests.get(url, stream=True)) as req:
            if req.status_code == 200:
                response = StreamingHttpResponse(req.iter_content(chunk_size=10000),
                                                 content_type='text/fasta')
                content_disposition = req.headers.get('content-disposition', '')
                if content_disposition:
                    response['Content-Disposition'] = content_disposition
                content_length = req.headers.get('content-length', '')
                if content_length:
                    response['Content-Length'] = content_length
                return response

    def stream_local_file():
        """
        Stream a results file hosted on the local server.
        """
        wrapper = FileWrapper(open(job.result, 'rb'))
        response = StreamingHttpResponse(wrapper, content_type=get_content_type())
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
                                          get_download_filename())
        response['Content-Length'] = os.path.getsize(job.result)
        return response

    messages = {
        400: {'message': 'Job id not specified'},
        404: {'message': 'Job not found'},
        202: {'message': 'File not ready, check back later'},
        500: {'message': 'Error while processing the job id'},
    }

    job_id = request.GET.get('job', '')
    if not job_id:
        status = 400
        return JsonResponse(messages[status], status=status)

    try:
        (job, remote_server) = get_job(job_id)

        if not job:
            status = 404
            return JsonResponse(messages[status], status=status)

        if job.is_finished:
            if remote_server:
                return stream_remote_file(remote_server)
            else:
                return stream_local_file()
        else:
            status = 202
            return JsonResponse(messages[status], status=status)
    except Exception as e:
        logger = logging.getLogger("django")
        logger.exception(e)

        status = 500
        return JsonResponse(messages[status], status=status)


@never_cache
def get_export_job_status(request):
    """
    Internal API.
    Get search export job status and associated metadata.

    HTTP responses:
    * 200 - job found
    * 400 - job id not provided in the url
    * 404 - job id not found in the queue
    * 500 - internal error
    """
    messages = {
        400: {'message': 'Job id not specified'},
        404: {'message': 'Job not found'},
        500: {'message': 'Error while processing the job id'},
    }

    job_id = request.GET.get('job', '')
    if not job_id:
        status = 400
        return JsonResponse(messages[status], status=status)

    try:
        job = get_job(job_id)[0]
        if job:
            data = {
                'id': job.id,
                'status': job.get_status(),
                'progress': 100 if job.is_finished else job.meta['progress'],
                'hits': job.meta['hits'],
                'enqueued_at': str(job.enqueued_at),
                'ended_at': str(job.ended_at),
                'query': job.meta['query'],
                'format': job.meta['format'],
                'expiration': job.meta['expiration'].strftime("%m/%d/%Y"),
            }
            return JsonResponse(data)
        else:
            status = 404
            return JsonResponse(messages[status], status=status)
    except Exception as e:
        logger = logging.getLogger("django")
        logger.exception(e)

        status = 500
        return JsonResponse(messages[status], status=status)


@never_cache
def submit_export_job(request):
    """
    Internal API.
    Export search results in different formats.

    Valid formats:
    * fasta (default)
    * json
    * list of RNAcentral ids

    HTTP responses:
    * 200 - job submitted
    * 400 - query not specified
    * 404 - format speciefied incorrectly
    * 500 - internal error
    """
    def get_hit_count(query):
        """
        Get the total number of results to be exported.
        """
        url = ''.join([settings.EBI_SEARCH_ENDPOINT,
                       '?query={query}',
                       '&start=0',
                       '&size=0',
                       '&format=json']).format(query=query)
        results = requests.get(url).json()
        hits = min(results['hitCount'], MAX_OUTPUT)
        return hits

    messages = {
        400: {'message': 'Query not specified'},
        404: {'message': 'Unrecognized format'},
        500: {'message': 'Error submitting the query'},
    }
    formats = ['fasta', 'json', 'list']

    query = request.GET.get('q', '')
    if not query:
        status = 400
        return JsonResponse(messages[status], status=status)

    _format = request.GET.get('format', 'fasta').lower()
    if _format not in formats:
        status = 404
        return JsonResponse(messages[status], status=status)

    try:
        queue = django_rq.get_queue()
        hits = get_hit_count(query)

        job = queue.enqueue_call(
            func=export_search_results,
            args=(query, _format, hits),
            timeout=MAX_RUN_TIME,
            result_ttl=EXPIRATION
        )
        job.meta['progress'] = 0
        job.meta['query'] = query
        job.meta['format'] = _format
        job.meta['hits'] = hits
        job.meta['expiration'] = datetime.datetime.now() + datetime.timedelta(seconds=EXPIRATION)
        job.save()
        return JsonResponse({'job_id': job.id})
    except Exception as e:
        logger = logging.getLogger("django")
        logger.exception(e)

        status = 500
        return JsonResponse(messages[status], status=status)
