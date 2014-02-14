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

from portal.models import Rna, Accession
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from apiv1.serializers import RnaNestedSerializer, AccessionSerializer, CitationSerializer, XrefSerializer, RnaFlatSerializer, RnaFastaSerializer
import django_filters
import re


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    Use this renderer instead of the original one to customize context variables.
    """

    def get_context(self, data, accepted_media_type, renderer_context):
        """
        """
        context = super(BrowsableAPIRenderer, self).get_context(data, accepted_media_type, renderer_context)
        context['new_variable'] = ['new variable']
        return context


class APIRoot(APIView):
    """
    This is the root of the RNAcentral API Version 1.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    permission_classes = (AllowAny,)

    def get(self, request, format=format):
        return Response({
            'rna': reverse('rna-list', request=request),
        })


class RnaFilter(django_filters.FilterSet):
    """
    Declare what fields can be filtered using django-filters
    """
    min_length = django_filters.NumberFilter(name="length", lookup_type='gte')
    max_length = django_filters.NumberFilter(name="length", lookup_type='lte')
    external_id = django_filters.CharFilter(name="xrefs__accession__external_id", distinct=True)

    class Meta:
        model = Rna
        fields = ['upi', 'md5', 'length', 'min_length', 'max_length', 'external_id']


class RnaFastaRenderer(renderers.BaseRenderer):
    """
    Render the fasta data received from RnaFastaSerializer.
    """
    media_type = 'text/fasta'
    format = 'fasta'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaFastaSerializer can return either a single entry or a list of entries.
        """
        if 'results' in data: # list of entries
            text = '# %i total entries, next page: %s, previous page: %s\n' % (data['count'], data['next'], data['previous'])
            for entry in data['results']:
                text += entry['fasta']
            return text
        else: # single entry
            return data['fasta']


class RnaMixin(object):
    """
    Mixin for additional functionality specific to Rna views.
    """
    def get_serializer_class(self):
        """
        Determine a serializer for RnaList and RnaDetail views.
        """
        if self.request.accepted_renderer.format == 'fasta':
            return RnaFastaSerializer

        flat = self.request.QUERY_PARAMS.get('flat', 'false')
        if re.match('true', flat, re.IGNORECASE):
            return RnaFlatSerializer
        return RnaNestedSerializer


class RnaList(RnaMixin, generics.ListAPIView):
    """
    Unique RNAcentral Sequences

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    permission_classes = (AllowAny,)
    filter_class = RnaFilter
    renderer_classes = (renderers.JSONRenderer, renderers.JSONPRenderer,
                        renderers.BrowsableAPIRenderer,
                        renderers.YAMLRenderer, RnaFastaRenderer)

    def _get_database_id(self):
        """
        Map the `database` parameter from the url to internal database ids
        """
        database = self.request.QUERY_PARAMS.get('database', None)
        if not database:
            pass
        elif re.match('ena', database, re.IGNORECASE):
            database = 1
        elif re.match('rfam', database, re.IGNORECASE):
            database = 2
        elif re.match('srpdb', database, re.IGNORECASE):
            database = 3
        elif re.match('mirbase', database, re.IGNORECASE):
            database = 4
        elif re.match('vega', database, re.IGNORECASE):
            database = 5
        elif re.match('tmrna_website', database, re.IGNORECASE):
            database = 6
        return database

    def get_queryset(self):
        """
        Manually filter against the `database` query parameter,
        use RnaFilter for other filtering operations.
        """
        queryset = Rna.objects.defer('seq_short', 'seq_long').select_related().all()
        database = self._get_database_id()
        if database:
            queryset = queryset.filter(xrefs__db=database)
        return queryset


class RnaDetail(RnaMixin, generics.RetrieveAPIView):
    """
    Unique RNAcentral Sequence

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    queryset = Rna.objects.select_related().all()
    renderer_classes = (renderers.JSONRenderer, renderers.JSONPRenderer,
                        renderers.BrowsableAPIRenderer,
                        renderers.YAMLRenderer, RnaFastaRenderer)


class XrefList(generics.ListAPIView):
    """
    List of cross-references for a particular RNA sequence.

    [API documentation](/api)
    """
    queryset = Rna.objects.select_related().all()
    serializer_class = RnaNestedSerializer

    def get(self, request, pk=None, format=None):
        """
        """
        rna = self.get_object()
        xrefs = rna.xrefs.all()
        serializer = XrefSerializer(xrefs, context={'request': request})
        return Response(serializer.data)


class AccessionView(generics.RetrieveAPIView):
    """
    API endpoint that allows single accessions to be viewed.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    queryset = Accession.objects.select_related().all()

    def get(self, request, pk, format=None):
        """
        Retrive individual accessions.
        """
        accession = self.get_object()
        serializer = AccessionSerializer(accession, context={'request': request})
        return Response(serializer.data)


class CitationView(generics.RetrieveAPIView):
    """
    API endpoint that allows the citations associated with
    each cross-reference to be viewed.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    queryset = Accession.objects.select_related().all()

    def get(self, request, pk, format=None):
        """
        Retrieve citations associated with a particular entry.
        This method is used to retrieve citations for the unique sequence view.
        """
        accession = self.get_object()
        citations = accession.refs.all()
        serializer = CitationSerializer(citations, context={'request': request})
        return Response(serializer.data)

