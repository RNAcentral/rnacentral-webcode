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

import django_rq
import gzip
import json
import os
import requests

from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache

from rq import get_current_job
from rest_framework import renderers

from apiv1.serializers import RnaFlatSerializer, RnaFastaSerializer
from apiv1.views import RnaFastaRenderer
from portal.models import Rna


def export_search_results(query, _format):
    """
    RQ worker function.
    Using the EBI search REST API
    * paginate over the results
    * extract RNAcentral ids
    * format the data
    * write it out to a local file.
    """
    # todo: switch to production endpoint
    endpoint = 'http://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral'
    job = get_current_job()

    def get_hit_count():
        """
        Get the total number of results to be exported.
        """
        hits = 0
        url = ''.join([endpoint,
                      '?query={query}',
                      '&start=0',
                      '&size=0',
                      '&format=json']).format(query=query)
        # todo error handling
        results = json.loads(requests.get(url).text)
        hits = results['hitCount']
        return hits

    def get_results_page(start, end):
        """
        Paginate over search results and record RNAcentral ids.
        """
        ids = []
        page_size = end - start
        url = ''.join([endpoint,
                      '?query={query}',
                      '&start={start}',
                      '&size={page_size}',
                      '&format=json']).format(query=query, start=start,
                                              page_size=page_size)
        # todo error handling
        data = json.loads(requests.get(url).text)
        for entry in data['entries']:
            ids.append(entry['id'])
        return ids

    def format_output(rnacentral_ids):
        """
        Given a list of RNAcentral ids, return the results
        in the specified format.
        """
        queryset = Rna.objects.filter(upi__in=rnacentral_ids).all()
        if _format == 'fasta':
            serializer = RnaFastaSerializer(queryset, many=True)
            renderer = RnaFastaRenderer()
        elif _format == 'json':
            serializer = RnaFlatSerializer(queryset, many=True)
            renderer = renderers.JSONRenderer() # todo: fix concatenated json documents
        output = renderer.render(serializer.data)
        return output

    def paginate_over_results():
        """
        Loop over the results and write out the data in an archive.
        """
        filename = os.path.join(settings.EXPORT_RESULTS_DIR,
                                '%s.%s.gz' % (job.id, _format))
        archive = gzip.open(filename, 'wb')
        start = 0
        page_size = 100
        while start < hits:
            max_end = start + page_size
            end = min(max_end, hits)
            rnacentral_ids = get_results_page(start, end)
            archive.write(format_output(rnacentral_ids))
            start = max_end
            job.meta['progress'] = max(float(start) / hits, 100)
            job.save()
        archive.close()
        return filename

    hits = get_hit_count()
    if hits == 0:
        data = 'no results'
    else:
        data = paginate_over_results()
    return data


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
        status = 404
        return JsonResponse(messages[status], status=status)

    if job.result:
        wrapper = FileWrapper(open(job.result, 'r'))
        response = HttpResponse(wrapper, content_type='text/fasta')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
                                          os.path.basename(job.result))
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
                'progress': job.meta['progress'],
                'enqueued_at': str(job.enqueued_at),
                'ended_at': str(job.ended_at),
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
    * csv

    HTTP responses:
    * 200 - job submitted
    * 400 - query not specified
    * 404 - format speciefied incorrectly
    * 500 - internal error
    """
    messages = {
        400: {'message': 'Query not specified'},
        404: {'message': 'Unrecognized format'},
        500: {'message': 'Error submitting the query'},
    }
    formats = ['fasta', 'json', 'csv']

    query = request.GET.get('q', '')
    if not query:
        status = 400
        return JsonResponse(messages[status], status=status)

    _format = request.GET.get('format', 'fasta').lower()
    if _format not in formats:
        status = 404
        return JsonResponse(messages[status], status=status)

    try:
        job = django_rq.enqueue(export_search_results, query, _format)
        job.meta['progress'] = 0
        job.save()
        return JsonResponse({'job_id': job.id})
    except:
        status = 500
        return JsonResponse(messages[status], status=status)
