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

from django.core.cache import cache
from portal.models import Rna
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import requests


class SequenceSearch(APIView):
    """
    Main class for handling RNAcentral sequence search.
    Relies on the ENA sequence search REST API.
    """
    permission_classes = (AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request):
        """
        """
        sequence = request.QUERY_PARAMS['sequence']
        if not sequence:
            return Response([])

        sequence = sequence.upper().replace('U','T')

        word_size = 12 # minimum hit length
        endpoints = {
            'search': 'http://jweb-1a:21160/ena/search/executeSearch?Sequence={sequence}',
            'status': 'http://jweb-1a:21160/ena/search/searchStatus',
            'results': 'http://jweb-1a:21160/ena/search/searchResults',
        }

        # r = requests.get(endpoints['search'].format(sequence=sequence))
        # statusUrl = r.text
        # print statusUrl
        # import time
        # time.sleep(1)
        # r = requests.get(statusUrl)
        # print r.text

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
