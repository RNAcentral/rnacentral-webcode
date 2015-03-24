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

from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from settings import MIN_LENGTH, MAX_LENGTH
from messages import messages
from utils import get_job, enqueue_job
from models import Results

from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes


@never_cache
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
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
        return Response(msg[status]['no_sequence'], status=status)

    if len(query) < MIN_LENGTH:
        status = 400
        return Response(msg[status]['too_short'], status=status)
    elif len(query) > MAX_LENGTH:
        status = 400
        return Response(msg[status]['too_long'], status=status)

    try:
        status = 201
        job_id = enqueue_job(query)
        url = request.build_absolute_uri(
            reverse('nhmmer-job-status') +
            '?id=%s' % job_id
        )
        data = {
            'id': job_id,
            'url': url,
        }
        return Response(data, status=status)
    except:
        status = 500
        return Response(msg[status], status=status)


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
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

    job_id = request.GET.get('id', '')
    if not job_id:
        status = 400
        return Response(msg[status], status=status)

    try:
        job = get_job(job_id)[0]
        if job:
            url = request.build_absolute_uri(
                reverse('nhmmer-job-results') +
                '?id=%s' % job_id
            )
            data = {
                'id': job.id,
                'status': job.get_status(),
                'enqueued_at': str(job.enqueued_at),
                'ended_at': str(job.ended_at),
                'expiration': job.meta['expiration'].strftime("%m/%d/%Y"),
                'url': url,
            }
            return Response(data)
        else:
            status = 404
            return Response(msg[status], status=status)
    except:
        status = 500
        return Response(msg[status], status=status)


class ResultsSerializer(serializers.ModelSerializer):
    """
    Django Rest Framework serializer class for
    listing nhmmer search results.
    """
    id = serializers.CharField(source='result_id')
    rnacentral_id = serializers.CharField(source='rnacentral_id')
    description = serializers.CharField(source='description')
    bias = serializers.CharField(source='bias')
    query_start = serializers.CharField(source='query_start')
    query_end = serializers.CharField(source='query_end')
    target_start = serializers.CharField(source='target_start')
    target_end = serializers.CharField(source='target_end')
    target_length = serializers.CharField(source='target_length')
    alignment = serializers.CharField(source='alignment')
    score = serializers.CharField(source='score')
    e_value = serializers.CharField(source='e_value')

    class Meta:
        model = Results
        fields = ('id', 'rnacentral_id', 'description', 'bias',
                  'query_start', 'query_end', 'target_start',
                  'target_end', 'target_length', 'alignment',
                  'score', 'e_value')


class ResultsView(generics.ListAPIView):
    """
    Django Rest Framework Generic View class
    for listing Nhmmer results based on query id.
    """
    permission_classes = (AllowAny,)
    serializer_class = ResultsSerializer

    def get_queryset(self):
        """
        Filter results by query id.
        """
        query_id = self.request.QUERY_PARAMS.get('id', None)
        return Results.objects.filter(query_id=query_id).\
                               order_by('id')
