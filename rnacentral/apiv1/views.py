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

from portal.models import Rna, Accession
from rest_framework import viewsets
from rest_framework.decorators import link
from rest_framework.response import Response
from apiv1.serializers import RnaSerializer, AccessionSerializer, RefSerializer, XrefSerializer
import django_filters


class RnaFilter(django_filters.FilterSet):
    database = django_filters.CharFilter(name="xrefs__db")
    min_length = django_filters.NumberFilter(name="length", lookup_type='gte')
    max_length = django_filters.NumberFilter(name="length", lookup_type='lte')
    external_id = django_filters.CharFilter(name="xrefs__accession__external_id", distinct=True)

    class Meta:
        model = Rna
        fields = ['upi', 'md5', 'length', 'database', 'min_length', 'max_length', 'external_id']


class RnaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Rna sequences to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    queryset = Rna.objects.defer('seq_long', 'seq_short').select_related().all()
    serializer_class = RnaSerializer
    paginate_by = 10
    filter_class = RnaFilter

    @link()
    def xrefs(self, request, pk=None):
        """
        Retrieve cross-references for a particular RNA sequence.
        """
        rna = self.get_object()
        xrefs = rna.xrefs.all()
        serializer = XrefSerializer(xrefs, context={'request': request})
        return Response(serializer.data)


class AccessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows cross-reference metadata to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    queryset = Accession.objects.select_related().all()
    serializer_class = AccessionSerializer
    paginate_by = 10

    @link()
    def citations(self, request, pk=None):
        """
        Retrieve citations associated with a particular entry.
        This method is used to retrieve citations for the unique sequence view.
        """
        accession = self.get_object()
        citations = accession.refs.all()
        serializer = RefSerializer(citations)
        return Response(serializer.data)

