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

"""
Docstrings of the classes exposed in urlpatters support markdown.
"""

from django.core.cache import cache
from portal.models import Rna
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
import re
import requests


class MetaSearch(APIView):
    """
    """
    permission_classes = (AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request):
        """
        accession    sequence_md5
        KF849944.1:14671..14739:tRNA 0026a4417938693f6af2993bc2920970
        """
        # return Response([{'rnacentral_id': 'test', 'xrefs': 10, 'species': 20, 'databases': 3}])

        # return Response(self.get_all_md5())

        taxid = request.QUERY_PARAMS['taxid']
        if not taxid:
            return Response([])

        url = 'http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq({taxid})%22&domain=noncoding&fields=sequence_md5,description&display=report&result=noncoding_release&sortfields=sequence_md5&offset=0&limit=30'
        r = requests.get(url.format(taxid=taxid))
        md5s = []
        descriptions = {}
        for i, line in enumerate(r.text.split('\n')):
            if i == 0 or line == '':
                continue
            (accession, md5, description) = line.split('\t')
            md5s.append(md5)
            descriptions[md5] = description
        md5s = set(md5s)
        rnas = Rna.objects.filter(md5__in=md5s).all()

        data = []
        for rna in rnas:
            data.append({
                'rnacentral_id': rna.upi,
                'species': rna.count_distinct_organisms(),
                'databases': rna.count_distinct_databases(),
                'xrefs': rna.count_xrefs(),
                'description': descriptions[rna.md5],
                'length': rna.length,
            })

        return Response(data)


    def get_all_md5(self):
        """
        Retrieve unique md5 values from the ENA paginated response.
        """
        cached = cache.get('9606')
        if cached:
            return {'count': len(cached)}

        URL = 'http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq(9606)%22&domain=noncoding&fields=sequence_md5&display=report&result=noncoding_release&sortfields=sequence_md5&limit={limit}&offset={offset}'
        LIMIT = pow(10, 5) # ENA maximum 100,000 entries per page
        offset = 0
        md5_result = set()
        while True:
            url = URL.format(limit=LIMIT, offset=offset)
            r = requests.get(url)
            for i, line in enumerate(r.text.split('\n')):
                if i and line:
                    (accession, md5) = line.split('\t')
                    md5_result.add(md5)
            if i < LIMIT + 1 : # LIMIT entries + 1 header row
                break
            offset += LIMIT
        cache.add('9606', md5_result)

        return {'count': len(md5_result)}
        # return Response({'count': len(md5_result)})

