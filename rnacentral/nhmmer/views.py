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
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache

from settings import MIN_LENGTH, MAX_LENGTH
from messages import messages
from utils import get_job, enqueue_job
from models import Results, Query

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
    bias = serializers.FloatField(source='bias')
    target_length = serializers.IntegerField(source='target_length')
    query_length = serializers.IntegerField(source='query_length')
    alignment = serializers.CharField(source='alignment')
    score = serializers.FloatField(source='score')
    e_value = serializers.FloatField(source='e_value')
    nts_count1 = serializers.IntegerField(source='nts_count1')
    nts_count2 = serializers.IntegerField(source='nts_count2')

    class Meta:
        model = Results
        fields = ('id', 'rnacentral_id', 'description', 'bias',
                  'target_length', 'query_length', 'alignment',
                  'score', 'e_value', 'match_count', 'gap_count',
                  'alignment_length', 'nts_count1', 'nts_count2',
                  'identity', 'query_coverage', 'target_coverage',
                  'gap_count')


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


class QuerySerializer(serializers.ModelSerializer):
    """
    Django Rest Framework serializer class for
    retrieving query details.
    """
    id = serializers.CharField(source='id')
    sequence = serializers.CharField(source='query')
    length = serializers.IntegerField(source='length')

    class Meta:
        model = Query
        fields = ('id', 'sequence', 'length')


class QueryView(generics.RetrieveAPIView):
    """
    Django Rest Framework view class for retrieving
    query details.
    """
    permission_classes = (AllowAny,)
    serializer_class = QuerySerializer

    def get_object(self):
        """
        Retrieve Query object.
        """
        query_id = self.request.QUERY_PARAMS.get('id', None)
        return get_object_or_404(Query, pk=query_id)
