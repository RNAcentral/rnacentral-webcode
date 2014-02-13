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
from rest_framework import generics
from rest_framework import renderers
from rest_framework.decorators import link
from rest_framework.response import Response
from apiv1.serializers import RnaSerializer, AccessionSerializer, CitationSerializer, XrefSerializer
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


class FastaRenderer(renderers.BaseRenderer):
    media_type = 'text/fasta'
    format = 'fasta'

    def render(self, rna, media_type=None, renderer_context=None):
        """
        Split long sequences by a fixed number of characters per line.
        """
        max_column = 80
        seq = rna.get_sequence()
        split_seq = ''
        i = 0
        while i < len(seq):
            split_seq += seq[i:i+max_column] + "\n"
            i += max_column
        fasta = "> %s\n%s" % (rna.upi, split_seq)
        return fasta


class RnaFastaView(generics.RetrieveAPIView):
    """
    Render RNA sequence in fasta format.
    """
    queryset = Rna.objects.all()
    renderer_classes = [FastaRenderer]

    def get(self, request, pk, format=None):
        """
        Retrive the Rna object and pass it on to the renderer.
        """
        rna = self.get_object()
        return Response(rna)


class AccessionView(generics.RetrieveAPIView):
    """
    API endpoint that allows single accessions to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    queryset = Accession.objects.select_related().all()
    serializer_class = AccessionSerializer

    def get(self, request, pk, format=None):
        """
        Retrive individual accessions.
        """
        accession = self.get_object()
        serializer = AccessionSerializer(accession)
        return Response(serializer.data)


class CitationView(generics.GenericAPIView):
    """
    API endpoint that allows the citations associated with
    each cross-reference to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    queryset = Accession.objects.select_related().all()

    def get(self, request, *args, **kwargs):
        """
        Retrieve citations associated with a particular entry.
        This method is used to retrieve citations for the unique sequence view.
        """
        accession = self.get_object()
        citations = accession.refs.all()
        serializer = CitationSerializer(citations)
        return Response(serializer.data)

