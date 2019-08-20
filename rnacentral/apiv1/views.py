from __future__ import print_function
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

from django.db.models import Min, Max, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, renderers, status
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
                              RawPublicationSerializer, RnaSecondaryStructureSerializer, \
                              RfamHitSerializer, SequenceFeatureSerializer, \
                              EnsemblAssemblySerializer, EnsemblInsdcMappingSerializer, ProteinTargetsSerializer, \
                              LncrnaTargetsSerializer, EnsemblComparaSerializer, SecondaryStructureSVGImageSerializer

from apiv1.renderers import RnaFastaRenderer, RnaGffRenderer, RnaGff3Renderer, RnaBedRenderer, SVGRenderer
from portal.models import Rna, RnaPrecomputed, Accession, Xref, Database, DatabaseStats, RfamHit, EnsemblAssembly,\
    EnsemblInsdcMapping, GenomeMapping, GenomicCoordinates, GoAnnotation, RelatedSequence, ProteinInfo, SequenceFeature,\
    SequenceRegion, EnsemblCompara, SecondaryStructureWithLayout
from portal.config.expert_databases import expert_dbs
from rnacentral.utils.pagination import Pagination, PaginatedRawQuerySet

"""
Docstrings of the classes exposed in urlpatterns support markdown.
"""

# maximum number of xrefs to use with prefetch_related
MAX_XREFS_TO_PREFETCH = 1000


class GenomeAnnotations(APIView):
    """
    Ensembl-like genome coordinates endpoint.

    [API documentation](/api)
    """
    # the above docstring appears on the API website

    permission_classes = (AllowAny,)

    def get(self, request, species, chromosome, start, end, format=None):
        start = start.replace(',', '')
        end = end.replace(',', '')

        try:
            assembly = EnsemblAssembly.objects.get(ensembl_url=species)
        except EnsemblAssembly.DoesNotExist:
            return Response([])

        regions = SequenceRegion.objects\
            .select_related('urs_taxid')\
            .prefetch_related('exons')\
            .filter(
                assembly=assembly,
                chromosome=chromosome,
                region_start__gte=start,
                region_stop__lte=end,
                urs_taxid__is_active=True
            )

        features = []
        for transcript in regions:
            features.append({
                'ID': transcript.region_name,
                'external_name': transcript.urs_taxid.id.split('_')[0],
                'taxid': assembly.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                'feature_type': 'transcript',
                'logic_name': 'RNAcentral',  # required by Genoverse
                'biotype': transcript.urs_taxid.rna_type,  # required by Genoverse
                'description': transcript.urs_taxid.short_description,
                'seq_region_name': transcript.chromosome,
                'strand': transcript.strand,
                'start': transcript.region_start,
                'end': transcript.region_stop,
                'databases': transcript.providing_databases
            })

            # exons
            for exon in transcript.exons.all():
                features.append({
                    'external_name': exon.id,
                    'ID': exon.id,
                    'taxid': assembly.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                    'feature_type': 'exon',
                    'Parent': transcript.region_name,
                    'logic_name': 'RNAcentral',  # required by Genoverse
                    'biotype': transcript.urs_taxid.rna_type,  # required by Genoverse
                    'seq_region_name': transcript.chromosome,
                    'strand': transcript.strand,
                    'start': exon.exon_start,
                    'end': exon.exon_stop,
                })

        return Response(features)


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


class SecondaryStructureSVGImage(generics.ListAPIView):
    """
    SVG image for an RNA sequence.
    """
    serializer_class = SecondaryStructureSVGImageSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (SVGRenderer,)

    def get(self, request, pk=None, format=None):
        rna = self.kwargs['pk']
        try:
            image = SecondaryStructureWithLayout.objects.get(urs=rna)
        except SecondaryStructureWithLayout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response(image.layout)


class RnaGenomeLocations(generics.ListAPIView):
    """
    List of distinct genomic locations, where a specific RNA
    is found in a specific species, extracted from xrefs.

    [API documentation](/api)
    """
    queryset = Rna.objects.select_related().all()

    def get(self, request, pk=None, taxid=None, format=None):
        # if assembly with this taxid is not found, just return empty locations list
        try:
            assembly = EnsemblAssembly.objects.get(taxid=taxid)  # this applies only to species-specific pages
        except EnsemblAssembly.DoesNotExist:
            return Response([])

        rna = self.get_object()
        urs_taxid = rna.upi + "_" + str(assembly.taxid)
        rna_precomputed = RnaPrecomputed.objects.get(id=urs_taxid)

        regions = SequenceRegion.objects.filter(urs_taxid=rna_precomputed)

        output = []
        for region in regions:
            output.append({
                'chromosome': region.chromosome,
                'strand': region.strand,
                'start': region.region_start,
                'end': region.region_stop,
                'identity': region.identity,
                'species': assembly.ensembl_url,
                'ucsc_db_id': assembly.assembly_ucsc,
                'ensembl_division': {
                    'name': assembly.division,
                    'url': 'http://' + assembly.subdomain
                },
                'ensembl_species_url': assembly.ensembl_url
            })

            exceptions = ['X', 'Y']
            if re.match(r'\d+', output[-1]['chromosome']) or output[-1]['chromosome'] in exceptions:
                output[-1]['ucsc_chromosome'] = 'chr' + output[-1]['chromosome']
            else:
                output[-1]['ucsc_chromosome'] = output[-1]['chromosome']

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

    def retrieve(self, request, *args, **kwargs):
        return super(ExpertDatabasesStatsViewSet, self).retrieve(request, *args, **kwargs)


class GenomesAPIViewSet(ListModelMixin, GenericViewSet):
    """API endpoint, presenting all E! assemblies, available in RNAcentral."""
    permission_classes = (AllowAny, )
    serializer_class = EnsemblAssemblySerializer
    pagination_class = Pagination
    queryset = EnsemblAssembly.objects.all().order_by('-ensembl_url')
    lookup_field = 'ensembl_url'


class RfamHitsAPIViewSet(generics.ListAPIView):
    """API endpoint with Rfam models that are found in an RNA."""
    permission_classes = (AllowAny, )
    serializer_class = RfamHitSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        return RfamHit.objects.filter(upi=upi).select_related('rfam_model').select_related('upi')

    def get_serializer_context(self):
        return {'taxid': self.kwargs['taxid']} if 'taxid' in self.kwargs else {}


class SequenceFeaturesAPIViewSet(generics.ListAPIView):
    """API endpoint with sequence features (CRS, mature miRNAs etc)"""
    permission_classes = (AllowAny, )
    serializer_class = SequenceFeatureSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs['pk']
        taxid = self.kwargs['taxid']
        return SequenceFeature.objects.filter(upi=upi, taxid=taxid, feature_name__in=["conserved_rna_structure", "mature_product"])


class EnsemblInsdcMappingView(APIView):
    """API endpoint, presenting mapping between E! and INSDC chromosome names."""
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):
        mapping = EnsemblInsdcMapping.objects.all().select_related()
        serializer = EnsemblInsdcMappingSerializer(mapping, many=True, context={request: request})
        return Response(serializer.data)


class RnaGoAnnotationsView(APIView):
    permission_classes = (AllowAny, )
    pagination_class = Pagination

    def get(self, request, pk, taxid, **kwargs):
        rna_id = pk + '_' + taxid
        taxid = int(taxid)
        annotations = GoAnnotation.objects.filter(rna_id=rna_id).\
            select_related('ontology_term', 'evidence_code')

        result = []
        for annotation in annotations:
            result.append({
                'rna_id': annotation.rna_id,
                'upi': pk,
                'taxid': taxid,
                'go_term_id': annotation.ontology_term.ontology_term_id,
                'go_term_name': annotation.ontology_term.name,
                'qualifier': annotation.qualifier,
                'evidence_code_id': annotation.evidence_code.ontology_term_id,
                'evidence_code_name': annotation.evidence_code.name,
                'assigned_by': annotation.assigned_by,
                'extensions': annotation.assigned_by or {},
            })

        return Response(result)


class EnsemblKaryotypeAPIView(APIView):
    """API endpoint, presenting E! karyotype for a given species."""
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, ensembl_url):
        try:
            assembly = EnsemblAssembly.objects.filter(ensembl_url=ensembl_url).prefetch_related('karyotype').first()
        except EnsemblAssembly.DoesNotExist:
            raise Http404

        return Response(assembly.karyotype.first().karyotype)


class ProteinTargetsView(generics.ListAPIView):
    """API endpoint, presenting ProteinInfo, related to given rna."""
    permission_classes = ()
    authentication_classes = ()
    pagination_class = Pagination
    serializer_class = ProteinTargetsSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        taxid = self.kwargs['taxid']

        # we select redundant {protein_info}.protein_accession because
        # otherwise django curses about lack of primary key in raw query
        protein_info_query = '''
            SELECT
                {related_sequence}.target_accession,
                {related_sequence}.source_accession,
                {related_sequence}.source_urs_taxid,
                {related_sequence}.methods,
                {protein_info}.protein_accession,
                {protein_info}.description,
                {protein_info}.label,
                {protein_info}.synonyms
            FROM {related_sequence}
            LEFT JOIN {protein_info}
            ON {protein_info}.protein_accession = {related_sequence}.target_accession
            WHERE {related_sequence}.relationship_type = 'target_protein'
              AND {related_sequence}.source_urs_taxid = '{pk}_{taxid}'
        '''.format(
            rna=Rna._meta.db_table,
            rna_precomputed=RnaPrecomputed._meta.db_table,
            related_sequence=RelatedSequence._meta.db_table,
            protein_info=ProteinInfo._meta.db_table,
            pk=pk,
            taxid=taxid
        )

        queryset = PaginatedRawQuerySet(protein_info_query, model=ProteinInfo)  # was: ProteinInfo.objects.raw(protein_info_query)
        return queryset


class LncrnaTargetsView(generics.ListAPIView):
    """API endpoint, presenting lncRNAs targeted by a given rna."""
    permission_classes = ()
    authentication_classes = ()
    pagination_class = Pagination
    serializer_class = LncrnaTargetsSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        taxid = self.kwargs['taxid']

        # we select redundant {protein_info}.protein_accession because
        # otherwise django curses about lack of primary key in raw query
        protein_info_query = '''
            SELECT
                {related_sequence}.source_accession,
                {related_sequence}.source_urs_taxid,
                {related_sequence}.methods,
                {related_sequence}.target_urs_taxid,
                {rna_precomputed}.short_description as target_rna_description,
                {related_sequence}.target_accession,
                {protein_info}.protein_accession,
                {protein_info}.description as target_ensembl_description,
                {protein_info}.label,
                {protein_info}.synonyms
            FROM {related_sequence}
            LEFT JOIN {rna_precomputed}
            ON target_urs_taxid = {rna_precomputed}.id
            LEFT JOIN protein_info
            ON {protein_info}.protein_accession = {related_sequence}.target_accession
            WHERE {related_sequence}.relationship_type = 'target_rna'
              AND {related_sequence}.source_urs_taxid = '{pk}_{taxid}'
            ORDER BY target_urs_taxid
        '''.format(
            rna_precomputed=RnaPrecomputed._meta.db_table,
            related_sequence=RelatedSequence._meta.db_table,
            protein_info=ProteinInfo._meta.db_table,
            pk=pk,
            taxid=taxid
        )
        queryset = PaginatedRawQuerySet(protein_info_query, model=ProteinInfo)
        return queryset


class LargerPagination(Pagination):
    page_size = 50
    ensembl_compara_url = None
    compara_status = None

    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
            'ensembl_compara_url': self.ensembl_compara_url,
            'ensembl_compara_status': self.ensembl_compara_status,
        })


class EnsemblComparaAPIViewSet(generics.ListAPIView):
    """API endpoint for related sequences identified by Ensembl Compara"""
    permission_classes = (AllowAny, )
    serializer_class = EnsemblComparaSerializer
    pagination_class = LargerPagination
    ensembl_transcript_id = ''

    def get_queryset(self):
        upi = self.kwargs['pk']
        taxid = self.kwargs['taxid']
        self_urs_taxid = upi + '_' + taxid
        urs_taxid = EnsemblCompara.objects.filter(urs_taxid__id=self_urs_taxid).first()
        if urs_taxid:
            self.ensembl_transcript_id = urs_taxid.ensembl_transcript_id
            return EnsemblCompara.objects.filter(homology_id=urs_taxid.homology_id)\
                                         .exclude(urs_taxid=self_urs_taxid)\
                                         .order_by('urs_taxid__description')\
                                         .all()
        else:
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        self.pagination_class.ensembl_compara_url = self.get_ensembl_compara_url()
        self.pagination_class.ensembl_compara_status = self.get_ensembl_compara_status()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({'data': serializer.data})

    def get_ensembl_compara_url(self):
        urs_taxid = self.kwargs['pk']+ '_' + self.kwargs['taxid']
        genome_region = SequenceRegion.objects.filter(urs_taxid__id=urs_taxid).first()
        if genome_region and self.ensembl_transcript_id:
            return 'http://www.ensembl.org/' + genome_region.assembly.ensembl_url + '/Gene/Compara_Tree?t=' + self.ensembl_transcript_id
        else:
            return None

    def get_ensembl_compara_status(self):
        urs_taxid = self.kwargs['pk']+ '_' + self.kwargs['taxid']

        rna_precomputed = RnaPrecomputed.objects.get(id=urs_taxid)
        if 'Ensembl' not in rna_precomputed.databases:
            return 'analysis not available'

        compara = EnsemblCompara.objects.filter(urs_taxid=urs_taxid).first()
        if compara:
            compara_count = EnsemblCompara.objects.filter(homology_id=compara.homology_id).count()

        if not compara or compara_count == 0:
            return 'RNA type not supported'

        if compara_count == 1:
            return 'not found'

        return 'found'
