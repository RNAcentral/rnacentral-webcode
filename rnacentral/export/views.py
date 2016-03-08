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

import datetime
import django_rq
import gzip
import json
import os
import requests

from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.text import get_valid_filename
from django.views.decorators.cache import never_cache

from contextlib import closing
from rq import get_current_job
from rest_framework import renderers

from apiv1.serializers import RnaFlatSerializer, RnaFastaSerializer
from apiv1.views import RnaFastaRenderer
from portal.models import Rna


EBI_SEARCH_ENDPOINT = 'http://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral'


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
        rnacentral_ids = []
        page_size = end - start
        url = ''.join([EBI_SEARCH_ENDPOINT,
                      '?query={query}',
                      '&start={start}',
                      '&size={page_size}',
                      '&format=json']).format(query=query, start=start,
                                              page_size=page_size)
        data = json.loads(requests.get(url).text)
        for entry in data['entries']:
            rnacentral_ids.append(entry['id'])
        return rnacentral_ids

    def format_output(rnacentral_ids):
        """
        Given a list of RNAcentral ids, return the results
        in the specified format.
        """
        if _format == 'list':
            return '\n'.join(rnacentral_ids) + '\n'                
        queryset = Rna.objects.filter(upi__in=rnacentral_ids).all()
        if _format == 'fasta':
            serializer = RnaFastaSerializer(queryset, many=True)
            renderer = RnaFastaRenderer()
            output = renderer.render(serializer.data)
        elif _format == 'json':
            serializer = RnaFlatSerializer(queryset, many=True)
            renderer = renderers.JSONRenderer()
            output = renderer.render(serializer.data)
            # omit opening and closing square brackets for easy concatenation
            output = output[1:-1]
            # make relative urls absolute
            output = output.replace('"/api/v1/', '"http://rnacentral.org/api/v1/')
        return output

    def paginate_over_results():
        """
        Paginate over the results and write out the data to an archive.
        JSON requires special treatment in order to concatenate
        multiple batches
        """
        filename = os.path.join(settings.EXPORT_RESULTS_DIR,
                                '%s.%s.gz' % (job.id, _format))
        archive = gzip.open(filename, 'wb')
        start = 0
        page_size = 100
        if _format == 'json':
            archive.write('[')
        while start < hits:
            max_end = start + page_size
            end = min(max_end, hits)
            rnacentral_ids = get_results_page(start, end)
            text = format_output(rnacentral_ids)
            archive.write(text)
            if _format == 'json' and end != hits:
                # join batches with commas except for the last iteration
                archive.write(',\n')
            start = max_end
            job.meta['progress'] = round(float(start) * 100 / hits, 2)
            job.save()
        if _format == 'json':
            archive.write(']')
        archive.close()
        return filename

    job = get_current_job()
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
    for queue_id, params in rq_queues.iteritems():
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
        max_length = 50
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
        wrapper = FileWrapper(open(job.result, 'r'))
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
    except:
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
    except:
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
        url = ''.join([EBI_SEARCH_ENDPOINT,
                      '?query={query}',
                      '&start=0',
                      '&size=0',
                      '&format=json']).format(query=query)
        results = json.loads(requests.get(url).text)
        return results['hitCount']

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

    expiration = 60*60*24*7
    max_run_time = 60*60
    try:
        queue = django_rq.get_queue()
        hits = get_hit_count(query)
        job = queue.enqueue_call(func=export_search_results,
                                 args=(query, _format, hits),
                                 timeout=max_run_time,
                                 result_ttl=expiration)
        job.meta['progress'] = 0
        job.meta['query'] = query
        job.meta['format'] = _format
        job.meta['hits'] = hits
        job.meta['expiration'] = datetime.datetime.now() + \
                                 datetime.timedelta(seconds=expiration)
        job.save()
        return JsonResponse({'job_id': job.id})
    except:
        status = 500
        return JsonResponse(messages[status], status=status)
