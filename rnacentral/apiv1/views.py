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

from django.core.paginator import Paginator
from django.http import Http404
from portal.models import Rna, Accession, Xref, Reference, Database
from rest_framework import generics
from rest_framework import renderers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from apiv1.serializers import RnaNestedSerializer, AccessionSerializer, CitationSerializer, PaginatedXrefSerializer, \
                              RnaFlatSerializer, RnaFastaSerializer, RnaGffSerializer, RnaGff3Serializer, RnaBedSerializer, \
                              RawCitationSerializer, RnaSpeciesSpecificSerializer
import django_filters
import re


def _get_xrefs_from_genomic_coordinates(species, chromosome, start, end):
    """
    Common function for retrieving xrefs based on genomic coordinates.
    """
    try:
        xrefs = Xref.objects.filter(accession__coordinates__chromosome=chromosome,
                                    accession__coordinates__primary_start__gte=start,
                                    accession__coordinates__primary_end__lte=end,
                                    accession__species=species.replace('_', ' ').capitalize(),
                                    deleted='N').\
                             all()
        return xrefs
    except:
        return []


class DasSources(APIView):
    """
    DAS `sources` method for determining supported capabilities.
    RNAcentral emulates the Homo_sapiens.GRCh38.gene Ensembl DAS source.
    """

    permission_classes = (AllowAny,)
    renderer_classes = (renderers.StaticHTMLRenderer,) # return the string unchanged

    def get(self, request):
        """
        Return the description of supported DAS sources.
        Example:
            http://www.ensembl.org/das/sources
        """
        urls = {
            'features': request.build_absolute_uri(reverse('das-features')),
            'stylesheet': request.build_absolute_uri(reverse('das-stylesheet')),
        }

        sources = """<?xml version="1.0" encoding="UTF-8" ?>
<SOURCES>
    <SOURCE uri="RNAcentral_GRCh38" title="RNAcentral" description="Unique RNAcentral Sequences">
        <MAINTAINER email="helpdesk@rnacentral.org" />
        <VERSION uri="RNAcentral_GRCh38" created="2014-03-06">
            <PROP name="label" value="RNAcentral" />
            <COORDINATES uri="http://www.dasregistry.org/dasregistry/coordsys/CS_DS311" taxid="9606" source="Chromosome" authority="GRCh" test_range="Y:26631479,26632610" version="38">GRCh_38,Chromosome,Homo sapiens</COORDINATES>
            <CAPABILITY type="das1:features" query_uri="{0}" />
            <CAPABILITY type="das1:stylesheet" query_uri="{1}" />
        </VERSION>
    </SOURCE>
</SOURCES>""".format(urls['features'], urls['stylesheet'])
        return Response(sources)


class DasStylesheet(APIView):
    """
    Das stylesheet for controlling the appearance of the RNAcentral Ensembl track.
    """

    permission_classes = (AllowAny,)
    renderer_classes = (renderers.StaticHTMLRenderer,) # return the string unchanged

    def get(self, request):
        """
        Style features created in DasFeatures.
        Example:
            http://www.ensembl.org/das/Homo_sapiens.GRCh38.transcript/stylesheet
        """
        stylesheet = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE DASSTYLE SYSTEM "http://www.biodas.org/dtd/dasstyle.dtd">
<DASSTYLE>
<STYLESHEET version="1.0">
  <CATEGORY id="group">
    <TYPE id="transcript:rnacentral">
      <GLYPH>
        <LINE>
          <HEIGHT>6</HEIGHT>
          <FGCOLOR>#104e8b</FGCOLOR>
          <STYLE>hat</STYLE>
        </LINE>
      </GLYPH>
    </TYPE>
  </CATEGORY>
  <CATEGORY id="transcription">
    <TYPE id="exon:non_coding:rnacentral">
      <GLYPH>
        <BOX>
          <HEIGHT>6</HEIGHT>
          <BGCOLOR>#ffffff</BGCOLOR>
          <FGCOLOR>#104e8b</FGCOLOR>
        </BOX>
      </GLYPH>
    </TYPE>
  </CATEGORY>
</STYLESHEET>
</DASSTYLE>"""
        return Response(stylesheet)


class DasFeatures(APIView):
    """
    DAS `features` method for retrieving genome annotations.
    """

    permission_classes = (AllowAny,)
    renderer_classes = (renderers.StaticHTMLRenderer, ) # return as an unmodified string

    def get(self, request):
        """
        Return genome annotation in DASGFF format.
        Does not use serializers and renderers because the XML has self-closing tags.
        Example:
        # get annotations
        http://www.ensembl.org/das/Homo_sapiens.GRCh38.transcript/features?segment=Y:25183643,25184773
        # no annotations, empty response
        http://www.ensembl.org/das/Homo_sapiens.GRCh38.transcript/features?segment=Y:100,120
        """

        def _parse_query_parameters():
            """
            Parse query parameters with genomic coordinates.
            Example: .../features?segment=chrY:1,200
            """
            regex = r'(?P<chromosome>(\d+|Y|X))\:(?P<start>\d+),(?P<end>\d+)'
            query_param = 'segment'
            m = re.search(regex, request.QUERY_PARAMS[query_param])
            if m:
                chromosome = m.group(1)
                start = m.group(3)
                end = m.group(4)
            else:
                chromosome = start = end = ''
            return (chromosome, start, end)

        def _format_segment():
            """
            Return a segment object containing exon features.
            """
            rnacentral_ids = []
            features = ''
            feature_types = { # defined in DasStylesheet
                'exon': 'exon:non_coding:rnacentral',
                'transcript': 'transcript:rnacentral',
            }
            for i, xref in enumerate(xrefs):
                rnacentral_id = xref.upi.upi
                if rnacentral_id not in rnacentral_ids:
                    rnacentral_ids.append(rnacentral_id)
                else:
                    continue
                coordinates = xref.get_genomic_coordinates()
                transcript_id = rnacentral_id + '_' + coordinates['chromosome'] + ':' + str(coordinates['start']) + '-' + str(coordinates['end'])
                rnacentral_url = request.build_absolute_uri(reverse('unique-rna-sequence', kwargs={'upi': rnacentral_id}))
                # exons
                for i, exon in enumerate(xref.accession.coordinates.all()):
                    exon_id = '_'.join([transcript_id, 'exon_' + str(i+1)])
                    features += """
  <FEATURE id="{exon_id}">
    <START>{start}</START>
    <END>{end}</END>
    <TYPE id="{feature_type}" category="transcription">{feature_type}</TYPE>
    <METHOD id="RNAcentral" />
    <SCORE>-</SCORE>
    <ORIENTATION>{strand}</ORIENTATION>
    <PHASE>.</PHASE>
    <GROUP id="{transcript_id}" type="{transcript_type}" label="{rnacentral_id}">
      <LINK href="{rnacentral_url}">{rnacentral_id}</LINK>
    </GROUP>
  </FEATURE>""".format(exon_id=exon_id,
                       start=exon.primary_start,
                       end=exon.primary_end,
                       feature_type=feature_types['exon'],
                       strand='+' if exon.strand > 0 else '-',
                       transcript_id=transcript_id,
                       rnacentral_id=rnacentral_id,
                       transcript_type=feature_types['transcript'],
                       rnacentral_url=rnacentral_url)

            segment = """
<SEGMENT id="{0}" start="{1}" stop="{2}">""".format(chromosome, start, end) + features + """
</SEGMENT>"""
            return segment

        def _format_das_response():
            """
            Add the header
            """
            return """<?xml version="1.0" standalone="no"?>
<!DOCTYPE DASGFF SYSTEM "http://www.biodas.org/dtd/dasgff.dtd">
<DASGFF>
<GFF version="1.0">""" + \
            segments + \
            """
</GFF>
</DASGFF>"""

        (chromosome, start, end) = _parse_query_parameters()
        # TODO: remove hardcoded species name
        xrefs = _get_xrefs_from_genomic_coordinates('Homo sapiens', chromosome, start, end)
        segments = _format_segment()
        das = _format_das_response()
        return Response(das)


class GenomeAnnotations(APIView):
    """
    Ensembl-like genome coordinates endpoint.

    [API documentation](/api)
    """
    # the above docstring appears on the API website

    permission_classes = (AllowAny,)

    def get(self, request, species, chromosome, start, end, format=None):
        """
        """
        start = start.replace(',','')
        end = end.replace(',','')

        xrefs = _get_xrefs_from_genomic_coordinates(species, chromosome, start, end)

        rnacentral_ids = []
        data = []
        for i, xref in enumerate(xrefs):
            rnacentral_id = xref.upi.upi
            # transcript object
            if rnacentral_id not in rnacentral_ids:
                rnacentral_ids.append(rnacentral_id)
            else:
                continue
            coordinates = xref.get_genomic_coordinates()
            transcript_id = rnacentral_id + '_' + coordinates['chromosome'] + ':' + str(coordinates['start']) + '-' + str(coordinates['end'])
            biotype = xref.accession.get_biotype()
            data.append({
                'ID': transcript_id,
                'external_name': rnacentral_id,
                'feature_type': 'transcript',
                'logic_name': 'RNAcentral', # required by Genoverse
                'biotype': biotype, # required by Genoverse
                'seq_region_name': chromosome,
                'strand': coordinates['strand'],
                'start': coordinates['start'],
                'end': coordinates['end'],
            })
            # exons
            exons = xref.accession.coordinates.all()
            for i, exon in enumerate(exons):
                exon_id = '_'.join([xref.accession.accession, 'exon_' + str(i)])
                if not exon.chromosome:
                    continue # some exons may not be mapped onto the genome (common in RefSeq)
                data.append({
                    'external_name': exon_id,
                    'ID': exon_id,
                    'feature_type': 'exon',
                    'Parent': transcript_id,
                    'logic_name': 'RNAcentral',  # required by Genoverse
                    'biotype': biotype, # required by Genoverse
                    'seq_region_name': chromosome,
                    'strand': exon.strand,
                    'start': exon.primary_start,
                    'end': exon.primary_end,
                })
        return Response(data)


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    Use this renderer instead of the original one to customize context variables.
    """

    def get_context(self, data, accepted_media_type, renderer_context):
        """
        """
        context = super(BrowsableAPIRenderer, self).get_context(data, accepted_media_type, renderer_context)
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
            'rna': reverse('rna-sequences', request=request),
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
        elif isinstance(data, list):
            text = []
            for entry in data:
                text.append(entry['fasta'])
            return ''.join(text)
        else: # single entry
            return data['fasta']


class RnaGffRenderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in GFF format received from RnaGffSerializer.
    """
    media_type = 'text/gff'
    format = 'gff'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaGffSerializer returns a single entry.
        """
        text = data['gff']
        if not text:
            text = '# Genomic coordinates not available'
        return text


class RnaGff3Renderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in GFF3 format received from RnaGff3Serializer.
    """
    media_type = 'text/gff3'
    format = 'gff3'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaGff3Serializer returns a single entry.
        """
        text = data['gff3']
        if not text or text == '##gff-version 3\n':
            text = '# Genomic coordinates not available'
        return text


class RnaBedRenderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in UCSC BED format received from RnaBedSerializer.
    """
    media_type = 'text/bed'
    format = 'bed'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaBedSerializer returns a single entry.
        """
        text = data['bed']
        if not text:
            text = '# Genomic coordinates not available'
        return text


class RnaMixin(object):
    """
    Mixin for additional functionality specific to Rna views.
    """
    def get_serializer_class(self):
        """
        Determine a serializer for RnaSequences and RnaDetail views.
        """
        if self.request.accepted_renderer.format == 'fasta':
            return RnaFastaSerializer
        elif self.request.accepted_renderer.format == 'gff':
            return RnaGffSerializer
        elif self.request.accepted_renderer.format == 'gff3':
            return RnaGff3Serializer
        elif self.request.accepted_renderer.format == 'bed':
            return RnaBedSerializer

        flat = self.request.QUERY_PARAMS.get('flat', 'false')
        if re.match('true', flat, re.IGNORECASE):
            return RnaFlatSerializer
        return RnaNestedSerializer


class RnaSequences(RnaMixin, generics.ListAPIView):
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

    def _get_database_id(self, db_name):
        """
        Map the `database` parameter from the url to internal database ids
        """
        for expert_database in Database.objects.all():
            if re.match(expert_database.label, db_name, re.IGNORECASE):
                return expert_database.id
        return None

    def get_queryset(self):
        """
        Manually filter against the `database` query parameter,
        use RnaFilter for other filtering operations.
        """
        db_name = self.request.QUERY_PARAMS.get('database', None)
        if db_name:
            db_id = self._get_database_id(db_name)
            if db_id:
                # `seq_long` **must** be deferred because in Oracle
                # `distinct` doesn't work with CLOB objects.
                queryset = Rna.objects.defer('seq_short', 'seq_long').\
                                       filter(xrefs__db=db_id).\
                                       distinct().\
                                       all()
            else:
                queryset = Rna.objects.none()
        else:
            flat = self.request.QUERY_PARAMS.get('flat', None)
            queryset = Rna.objects.all()
            if flat:
                queryset = queryset.prefetch_related('xrefs','xrefs__accession')
        return queryset


class RnaDetail(RnaMixin, generics.RetrieveAPIView):
    """
    Unique RNAcentral Sequence

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    permission_classes = (AllowAny,)
    renderer_classes = (renderers.JSONRenderer, renderers.JSONPRenderer,
                        renderers.BrowsableAPIRenderer, renderers.YAMLRenderer,
                        RnaFastaRenderer, RnaGffRenderer, RnaGff3Renderer, RnaBedRenderer)

    def get_queryset(self):
        """
        Prefetch related objects only when `flat=True`.
        """
        flat = self.request.QUERY_PARAMS.get('flat', None)
        queryset = Rna.objects.all()
        if flat:
            queryset = queryset.prefetch_related('xrefs','xrefs__accession')
        return queryset


class RnaSpeciesSpecificView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving species-specific details
    about Unique RNA Sequences.

    [API documentation](/api)
    """
    # the above docstring appears on the API website

    """
    This endpoint is used by Protein2GO.
    Contact person: Tony Sawford.
    """
    queryset = Rna.objects.all()

    def get(self, request, pk, taxid, format=None):
        """
        Respond to Get requests.
        """
        rna = self.get_object()
        xrefs = rna.xrefs.filter(taxid=taxid)
        if not xrefs:
            raise Http404
        serializer = RnaSpeciesSpecificSerializer(rna, context={
            'request': request,
            'xrefs': xrefs,
            'taxid': taxid,
        })
        return Response(serializer.data)


class XrefList(generics.ListAPIView):
    """
    List of cross-references for a particular RNA sequence.

    [API documentation](/api)
    """
    queryset = Rna.objects.select_related().all()

    def get(self, request, pk=None, format=None):
        """
        Get a paginated list 
        """
        page = request.QUERY_PARAMS.get('page', 1)
        page_size = request.QUERY_PARAMS.get('page_size', 100)

        rna = self.get_object()
        xrefs = rna.get_xrefs()
        paginator_xrefs = Paginator(xrefs, page_size)
        xrefs_page = paginator_xrefs.page(page)
        serializer = PaginatedXrefSerializer(xrefs_page, context={'request': request})
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


class RnaCitationsView(generics.ListAPIView):
    """
    API endpoint that allows the citations associated with
    each Unique RNA Sequence to be viewed.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    permission_classes = (AllowAny,)
    serializer_class = RawCitationSerializer

    def get_queryset(self):
        """
        """
        upi = self.kwargs['pk']
        return list(Rna.objects.get(upi=upi).get_publications())
