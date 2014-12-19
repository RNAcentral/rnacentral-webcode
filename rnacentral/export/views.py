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
import gzip
import json
import os
import requests
import socket

from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
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
        elif _format == 'list':
            output = '\n'.join(rnacentral_ids) + '\n'
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


@never_cache
def download_search_result_file(request):
    """
    Internal API.
    Download a file with metadata search results given a job id.
    To control memory usage the file is returned in small chunks via Django.

    HTTP responses:
    * 400 - job id not provided in the url
    * 404 - job id not found in the queue
    * 202 - result is not ready yet
    * 200 - result is ready
    """
    messages = {
        400: {'message': 'Job id not specified'},
        404: {'message': 'Job not found'},
        202: {'message': 'File not ready, check back later'},
    }

    job_id = request.GET.get('job', '')
    if not job_id:
        status = 400
        return JsonResponse(messages[status], status=status)

    queue = django_rq.get_queue()
    job = queue.fetch_job(job_id)

    if not job:
        this_host = socket.gethostname()
        hosts = getattr(settings, "HOSTS", [])
        for host in hosts:
            if host == this_host:
                continue
            url = ''.join(['http://', host, request.get_full_path()])
            with closing(requests.get(url, stream=True)) as req:
                if req.status_code == 200:
                    response = StreamingHttpResponse(req.iter_content(chunk_size=10000),
                                                     content_type='text/fasta')
                    response['Content-Disposition'] = req.headers['content-disposition']
                    response['Content-Length'] = req.headers['content-length']
                    return response
        status = 404
        return JsonResponse(messages[status], status=status)

    if job.is_finished:
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

        wrapper = FileWrapper(open(job.result, 'r'))
        response = StreamingHttpResponse(wrapper, content_type='text/fasta')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
                                          get_download_filename())
        response['Content-Length'] = os.path.getsize(job.result)
        return response
    else:
        status = 202
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
    def poll_remote_hosts():
        """
        If the job is not found in the local queue,
        query all remote servers.

        As load balancer can direct API requests to servers
        other than the one hosting the job, it is desirable
        to make load balancing transparent to the API.
        """
        remote_data = None
        this_host = socket.gethostname()
        hosts = getattr(settings, "HOSTS", [])
        for host in hosts:
            if host == this_host:
                continue
            url = ''.join(['http://', host, request.get_full_path()])
            req = requests.get(url)
            if req.status_code == 200:
                data = req.json()
                if 'id' in data and 'message' not in data: # job found
                    remote_data = data
                    break
        return remote_data

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
        queue = django_rq.get_queue()
        job = queue.fetch_job(job_id)
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
            # job not found in the local queue, try other servers
            remote_data = poll_remote_hosts()
            if remote_data:
                return JsonResponse(remote_data)
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
        job.meta['expiration'] = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
        job.save()
        return JsonResponse({'job_id': job.id})
    except:
        status = 500
        return JsonResponse(messages[status], status=status)
