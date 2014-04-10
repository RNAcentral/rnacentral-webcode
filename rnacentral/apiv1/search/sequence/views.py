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

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from apiv1.search.sequence.rest_client import ENASequenceSearchClient,
    SequenceSearchError


@api_view(['GET'])
@permission_classes((AllowAny,))
def search(request):
    """
    Placeholder endpoint for testing.
    """
    try:
        sequence = request.QUERY_PARAMS['sequence']
    except:
        return Response([])

    data = [{
                'alignment': """
    Query 47        TTCCTCATTATGGGGTGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGA 106
                    |||||  |||  || |||||||||||||||||||||||||||||||||||||||||||||
    Sbjct 12473741  TTCCTG-TTACAGG-TGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGA 12473798

    Query 107       CATTCTGGGGTCCCAGTTCAAGTATTTTCCAATGTGAGTCAAGGTGAACCAGAGCCTGAA 166
                    |||||||||||||||||||||||||||||||| |||||||||||||||||||||||||||
    Sbjct 12473799  CATTCTGGGGTCCCAGTTCAAGTATTTTCCAACGTGAGTCAAGGTGAACCAGAGCCTGAA 12473858""".replace('T', 'U'),
                'accession': 'test accession',
                'description': 'test description',
            },{
                'alignment': """
    Query 47        TTCCTCATTATGGGGTGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGA 106
                    |||||  |||  || |||||||||||||||||||||||||||||||||||||||||||||
    Sbjct 12473741  TTCCTG-TTACAGG-TGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGA 12473798

    Query 107       CATTCTGGGGTCCCAGTTCAAGTATTTTCCAATGTGAGTCAAGGTGAACCAGAGCCTGAA 166
                    |||||||||||||||||||||||||||||||| |||||||||||||||||||||||||||
    Sbjct 12473799  CATTCTGGGGTCCCAGTTCAAGTATTTTCCAACGTGAGTCAAGGTGAACCAGAGCCTGAA 12473858""".replace('T', 'U'),
                'accession': 'test accession 2',
                'description': 'test description 2',
            }]
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def submit(request):
    """
    Submit a sequence and get `job_id` and `jsession_id`
    for retrieving results.
    """
    job_id = jsession_id = message = None
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        sequence = request.QUERY_PARAMS['sequence']
    except:
        message = '`sequence` query parameter is required'
        code = status.HTTP_400_BAD_REQUEST
    else:
        client = ENASequenceSearchClient()
        try:
            (job_id, jsession_id) = client.submit_query(sequence)
        except SequenceSearchError, e:
            message = e.message
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            message = 'Query successfully submitted'
            code = status.HTTP_200_OK
    data = {
        'job_id': job_id,
        'jsession_id': jsession_id,
        'message': message,
    }
    return Response(data, status=code)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_status(request):
    """
    Check the query status using `job_id` and `jsession_id`
    query parameters.

    Returns a status `message` and a `status` code, which can be:

    * `Done`
    * `In progress`
    * `Failed`
    """
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        job_id = request.QUERY_PARAMS['job_id']
        jsession_id = request.QUERY_PARAMS['jsession_id']
    except:
        message = '`job_id` and `jsession_id` query parameters are required'
        code = status.HTTP_400_BAD_REQUEST
    else:
        client = ENASequenceSearchClient()
        try:
            query_status = client.get_status(job_id, jsession_id)
        except SequenceSearchError, e:
            query_status = 'Failed'
            message = e.message
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            message = 'No errors'
            code = status.HTTP_200_OK
    data = {
        'status': query_status,
        'message': message,
    }
    return Response(data, status=code)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_results(request):
    pass




