"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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
import re
import warnings
from itertools import chain

from django.db.models import Min, Max
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework import renderers
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework_yaml.renderers import YAMLRenderer

from apiv1.serializers import RnaNestedSerializer, AccessionSerializer, CitationSerializer, XrefSerializer, \
                              RnaFlatSerializer, RnaFastaSerializer, RnaGffSerializer, RnaGff3Serializer, RnaBedSerializer, \
                              RnaSpeciesSpecificSerializer, ExpertDatabaseStatsSerializer, \
                              RawPublicationSerializer, RnaSecondaryStructureSerializer, RfamHitSerializer, \
                              EnsemblInsdcMappingSerializer
from apiv1.renderers import RnaFastaRenderer, RnaGffRenderer, RnaGff3Renderer, RnaBedRenderer
from portal.models import Rna, Accession, Xref, Database, DatabaseStats, RfamHit, EnsemblInsdcMapping
from portal.config.genomes import genomes, url2db, db2url, SpeciesNotInGenomes, get_taxid_from_species, get_ensembl_division, get_ensembl_species_url, get_ucsc_db_id
from portal.config.expert_databases import expert_dbs
from rnacentral.utils.pagination import Pagination

"""
Docstrings of the classes exposed in urlpatterns support markdown.
"""

# maximum number of xrefs to use with prefetch_related
MAX_XREFS_TO_PREFETCH = 1000


def _get_xrefs_from_genomic_coordinates(species, chromosome, start, end):
    """Common function for retrieving xrefs based on genomic coordinates."""
    try:
        xrefs = Xref.default_objects.filter(
            accession__coordinates__chromosome=chromosome,
            accession__coordinates__primary_start__gte=start,
            accession__coordinates__primary_end__lte=end,
            accession__species=url2db(species),
            deleted='N'
        ).all()

        return xrefs
    except Exception as e:
        return []


class GenomeAnnotations(APIView):
    """
    Ensembl-like genome coordinates endpoint.

    [API documentation](/api)
    """
    # the above docstring appears on the API website

    permission_classes = (AllowAny,)

    def get(self, request, species, chromosome, start, end, format=None):
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
            biotype = xref.upi.precomputed.filter(taxid=xref.taxid)[0].rna_type  # used to be biotype = xref.accession.get_biotype()
            description = xref.upi.precomputed.filter(taxid=xref.taxid)[0].description

            data.append({
                'ID': transcript_id,
                'external_name': rnacentral_id,
                'taxid': xref.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                'feature_type': 'transcript',
                'logic_name': 'RNAcentral',  # required by Genoverse
                'biotype': biotype,  # required by Genoverse
                'description': description,
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
                    continue  # some exons may not be mapped onto the genome (common in RefSeq)
                data.append({
                    'external_name': exon_id,
                    'ID': exon_id,
                    'taxid': xref.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                    'feature_type': 'exon',
                    'Parent': transcript_id,
                    'logic_name': 'RNAcentral',  # required by Genoverse
                    'biotype': biotype,  # required by Genoverse
                    'seq_region_name': chromosome,
                    'strand': exon.strand,
                    'start': exon.primary_start,
                    'end': exon.primary_end,
                })
        return Response(data)


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


class RnaFilter(filters.FilterSet):
    """Declare what fields can be filtered using django-filters"""
    min_length = filters.NumberFilter(name="length", lookup_expr='gte')
    max_length = filters.NumberFilter(name="length", lookup_expr='lte')
    external_id = filters.CharFilter(name="xrefs__accession__external_id", distinct=True)
    database = filters.CharFilter(name="xrefs__accession__database")

    class Meta:
        model = Rna
        fields = ['upi', 'md5', 'length', 'min_length', 'max_length', 'external_id', 'database']


class RnaMixin(object):
    """Mixin for additional functionality specific to Rna views."""
    def get_serializer_class(self):
        """Determine a serializer for RnaSequences and RnaDetail views."""
        if self.request.accepted_renderer.format == 'fasta':
            return RnaFastaSerializer
        elif self.request.accepted_renderer.format == 'gff':
            return RnaGffSerializer
        elif self.request.accepted_renderer.format == 'gff3':
            return RnaGff3Serializer
        elif self.request.accepted_renderer.format == 'bed':
            return RnaBedSerializer

        flat = self.request.query_params.get('flat', 'false')
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
    renderer_classes = (renderers.JSONRenderer, JSONPRenderer,
                        renderers.BrowsableAPIRenderer,
                        YAMLRenderer, RnaFastaRenderer)
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        """
        List view in Django Rest Framework is responsible
        for displaying entries from the queryset.
        Here the view is overridden in order to avoid
        performance bottlenecks.

        * estimate the number of xrefs for each Rna
        * prefetch_related only for Rnas with a small number of xrefs
        * do not attempt to optimise entries with a large number of xrefs
          letting Django hit the database one time for each xref
        * flat serializer limits the total number of displayed xrefs
        """
        # begin DRF base code
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        # end DRF base code

        # begin RNAcentral override: use prefetch_related where possible
        flat = self.request.query_params.get('flat', None)
        if flat:
            to_prefetch = []
            no_prefetch = []
            for rna in page:
                if rna.xrefs.count() <= MAX_XREFS_TO_PREFETCH:
                    to_prefetch.append(rna.upi)
                else:
                    no_prefetch.append(rna.upi)

            prefetched = self.filter_queryset(Rna.objects.filter(upi__in=to_prefetch).prefetch_related('xrefs__accession').all())
            not_prefetched = self.filter_queryset(Rna.objects.filter(upi__in=no_prefetch).all())

            result_list = list(chain(prefetched, not_prefetched))
            page.object_list = result_list  # override data while keeping the rest of the pagination object
        # end RNAcentral override

        # begin DRF base code
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        # end DRF base code

    def _get_database_id(self, db_name):
        """Map the `database` parameter from the url to internal database ids"""
        for expert_database in Database.objects.all():
            if re.match(expert_database.label, db_name, re.IGNORECASE):
                return expert_database.id
        return None

    def get_queryset(self):
        """
        Manually filter against the `database` query parameter,
        use RnaFilter for other filtering operations.
        """
        db_name = self.request.query_params.get('database', None)
        # `seq_long` **must** be deferred in order for filters to work
        queryset = Rna.objects.defer('seq_long')
        if db_name:
            db_id = self._get_database_id(db_name)
            if db_id:
                return queryset.filter(xrefs__db=db_id).distinct().all()
            else:
                return Rna.objects.none()
        return queryset.all()


class RnaDetail(RnaMixin, generics.RetrieveAPIView):
    """
    Unique RNAcentral Sequence

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    queryset = Rna.objects.all()
    renderer_classes = (renderers.JSONRenderer, JSONPRenderer,
                        renderers.BrowsableAPIRenderer, YAMLRenderer,
                        RnaFastaRenderer, RnaGffRenderer, RnaGff3Renderer, RnaBedRenderer)

    def get_object(self):
        """
        Prefetch related objects only when `flat=True`
        and the number of xrefs is not too large.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        rna = get_object_or_404(queryset, **filter_kwargs)

        flat = self.request.query_params.get('flat', None)
        if flat and rna.xrefs.count() <= MAX_XREFS_TO_PREFETCH:
            queryset = queryset.prefetch_related('xrefs', 'xrefs__accession')
            return get_object_or_404(queryset, **filter_kwargs)
        else:
            return rna


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
    serializer_class = XrefSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        return Rna.objects.get(upi=upi).get_xrefs()


class XrefsSpeciesSpecificList(generics.ListAPIView):
    """
    List of cross-references for a particular RNA sequence in a specific species.

    [API documentation](/api)
    """
    serializer_class = XrefSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        taxid = self.kwargs['taxid']
        return Rna.objects.get(upi=upi).get_xrefs(taxid=taxid)


class SecondaryStructureSpeciesSpecificList(generics.ListAPIView):
    """
    List of secondary structures for a particular RNA sequence in a specific species.

    [API documentation](/api)
    """
    queryset = Rna.objects.all()

    def get(self, request, pk=None, taxid=None, format=None):
        """Get a paginated list of cross-references"""
        rna = self.get_object()
        serializer = RnaSecondaryStructureSerializer(rna, context={
            'taxid': taxid,
        })
        return Response(serializer.data)


class RnaGenomeLocations(generics.ListAPIView):
    """
    List of distinct genomic locations, where a specific RNA
    is found in a specific species, extracted from xrefs.

    [API documentation](/api)
    """
    queryset = Rna.objects.select_related().all()

    def get(self, request, pk=None, taxid=None, format=None):
        """Paginated list of genome locations"""
        locations = []

        rna = self.get_object()
        xrefs = rna.get_xrefs(taxid=taxid)
        for xref in xrefs:
            if xref.accession.coordinates.exists() and xref.accession.coordinates.all()[0].chromosome:
                data = {
                    'chromosome': xref.accession.coordinates.all()[0].chromosome,
                    'strand': xref.accession.coordinates.all()[0].strand,
                    'start': xref.accession.coordinates.all().aggregate(Min('primary_start'))['primary_start__min'],
                    'end': xref.accession.coordinates.all().aggregate(Max('primary_end'))['primary_end__max'],
                    'species': db2url(xref.accession.species),
                    'ucsc_db_id': xref.get_ucsc_db_id(),
                    'ensembl_division': xref.get_ensembl_division(),
                    'ensembl_species_url': xref.accession.get_ensembl_species_url()
                }

                exceptions = ['X', 'Y']
                if re.match(r'\d+', data['chromosome']) or data['chromosome'] in exceptions:
                    data['ucsc_chromosome'] = 'chr' + data['chromosome']
                else:
                    data['ucsc_chromosome'] = data['chromosome']

                if data not in locations:
                    locations.append(data)

        return Response(locations)


class RnaGenomeMappings(generics.ListAPIView):
    queryset = Rna.objects.select_related().all()

    def get(self, request, pk=None, taxid=None, format=None):
        rna = self.get_object()
        mappings = rna.genome_mappings.filter(taxid=taxid)\
                                      .values('region_id', 'strand', 'chromosome', 'taxid')\
                                      .annotate(Min('start'), Max('stop'))
        print(mappings)

        species = rna.xrefs.first().accession.species

        output = []
        for mapping in mappings:
            data = {
                'chromosome': mapping["chromosome"],
                'strand': 1 if mapping["strand"] == '+' else -1,  # convert +/- to 1/-1
                'start': mapping["start__min"],
                'end': mapping["stop__max"],
                'species': db2url(species),
                'ucsc_db_id': get_ucsc_db_id(mapping["taxid"]),
                'ensembl_division': get_ensembl_division(species),
                'ensembl_species_url': get_ensembl_species_url(species, rna.xrefs.first().accession)
            }
            output.append(data)

        return Response(output)


class AccessionView(generics.RetrieveAPIView):
    """
    API endpoint that allows single accessions to be viewed.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    queryset = Accession.objects.select_related().all()
    serializer_class = AccessionSerializer


class CitationsView(generics.ListAPIView):
    """
    API endpoint that allows the citations associated with
    a particular cross-reference to be viewed.

    [API documentation](/api)
    """
    serializer_class = CitationSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Accession.objects.select_related().get(pk=pk).refs.all()


class RnaPublicationsView(generics.ListAPIView):
    """
    API endpoint that allows the citations associated with
    each Unique RNA Sequence to be viewed.

    [API documentation](/api)
    """
    # the above docstring appears on the API website
    permission_classes = (AllowAny, )
    serializer_class = RawPublicationSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        taxid = self.kwargs['taxid'] if 'taxid' in self.kwargs else None
        return Rna.objects.get(upi=upi).get_publications(taxid)  # this is actually a list


class ExpertDatabasesAPIView(APIView):
    """
    API endpoint describing expert databases, comprising RNAcentral.

    [API documentation](/api)
    """
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):
        """The data from configuration JSON and database are combined here."""

        def _normalize_expert_db_label(expert_db_label):
            """Capitalizes db label (and accounts for special cases)"""
            if re.match('tmrna-website', expert_db_label, flags=re.IGNORECASE):
                expert_db_label = 'TMRNA_WEB'
            else:
                expert_db_label = expert_db_label.upper()
            return expert_db_label

        # e.g. { "TMRNA_WEB": {'name': 'tmRNA Website', 'label': 'tmrna-website', ...}}
        databases = { db['descr']:db for db in Database.objects.values() }

        # update config.expert_databases json with Database table objects
        for db in expert_dbs:
            normalized_label = _normalize_expert_db_label(db['label'])
            if normalized_label in databases:
                db.update(databases[normalized_label])

        return Response(expert_dbs)

    # def get_queryset(self):
    #     expert_db_name = self.kwargs['expert_db_name']
    #     return Database.objects.get(expert_db_name).references


class ExpertDatabasesStatsViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    API endpoint with statistics of databases, comprising RNAcentral.

    [API documentation](/api)
    """
    queryset = DatabaseStats.objects.all()
    serializer_class = ExpertDatabaseStatsSerializer
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        return super(ExpertDatabasesStatsViewSet, self).list(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ExpertDatabasesStatsViewSet, self).retrieve(request, *args, **kwargs)


class GenomesAPIView(APIView):
    """API endpoint, presenting genomes available for display in RNAcentral genome browser."""
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):
        sorted_genomes = sorted(genomes, key=lambda x: x['species'])
        return Response(sorted_genomes)


class RfamHitsAPIViewSet(generics.ListAPIView):
    """API endpoint with Rfam models that are found in an RNA."""
    permission_classes = (AllowAny, )
    serializer_class = RfamHitSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        return RfamHit.objects.filter(upi=upi).select_related('rfam_model')


class EnsemblInsdcMappingView(APIView):
    """API endpoint, presenting mapping between E! and INSDC chromosome names."""
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):
        mapping = EnsemblInsdcMapping.objects.all().select_related()
        serializer = EnsemblInsdcMappingSerializer(mapping, many=True, context={request: request})
        return Response(serializer.data)
