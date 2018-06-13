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
                              EnsemblAssemblySerializer, EnsemblInsdcMappingSerializer
from apiv1.renderers import RnaFastaRenderer, RnaGffRenderer, RnaGff3Renderer, RnaBedRenderer
from portal.models import Rna, RnaPrecomputed, Accession, Xref, Database, DatabaseStats, RfamHit, EnsemblAssembly,\
    EnsemblInsdcMapping, GenomeMapping, GoAnnotation, url2db, db2url
from portal.config.expert_databases import expert_dbs
from rnacentral.utils.pagination import Pagination

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

        # get features from xrefs and from genome mappings
        xrefs_features = features_from_xrefs(species, chromosome, start, end)
        mappings_features = features_from_mappings(species, chromosome, start, end)

        # filter out features from genome mappings that duplicate features from xrefs
        features = xrefs_features[:]
        for mappings_feature in mappings_features:
            duplicate = False  # flag
            for xrefs_feature in xrefs_features:
                if (xrefs_feature['start'] == mappings_feature['start'] and
                   xrefs_feature['end'] == mappings_feature['end'] and
                   str(xrefs_feature['strand']) == str(mappings_feature['strand']) and
                   xrefs_feature['seq_region_name'] == mappings_feature['seq_region_name'] and
                   xrefs_feature['taxid'] == mappings_feature['taxid'] and
                   xrefs_feature['external_name'] == mappings_feature['external_name']):
                    duplicate = True
                    break

            if not duplicate:
                features.append(mappings_feature)

        return Response(features)


def _species2taxid(species):
    """This is a terribly indirect way to get taxid by species"""
    accession = Accession.objects.filter(species=url2db(species)).first()
    xrefs = Xref.default_objects.filter(accession=accession, deleted='N').all()
    if len(xrefs) != 0:
        taxid = xrefs[0].taxid
    else:
        xrefs = Xref.objects.filter(accession=accession).all()
        taxid = xrefs[0].taxid

    return taxid


def features_from_xrefs(species, chromosome, start, end):
    try:
        xrefs = Xref.default_objects.filter(
            accession__coordinates__chromosome=chromosome,
            accession__coordinates__primary_start__gte=start,
            accession__coordinates__primary_end__lte=end,
            accession__species=url2db(species),
            deleted='N'
        ).select_related('upi', 'accession', 'db').prefetch_related('upi__precomputed')
    except Xref.DoesNotExist:
        xrefs = []

    upi2data = {}
    data = []
    for i, xref in enumerate(xrefs):
        upi = xref.upi.upi

        # create only one transcript object per upi
        if upi not in upi2data:
            taxid = _species2taxid(species)
            xrefs = Xref.default_objects.filter(upi=upi, taxid=taxid, deleted='N').select_related('db').all()
            databases = list(set([x.db.display_name for x in xrefs]))
            databases.sort()
            coordinates = xref.get_genomic_coordinates()
            transcript_id = upi + '_' + coordinates['chromosome'] + ':' + str(coordinates['start']) + '-' + str(coordinates['end'])
            biotype = xref.upi.precomputed.filter(taxid=xref.taxid)[0].rna_type  # used to be biotype = xref.accession.get_biotype()
            description = xref.upi.precomputed.filter(taxid=xref.taxid)[0].description

            transcript = {
                'ID': transcript_id,
                'external_name': upi,
                'taxid': xref.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                'feature_type': 'transcript',
                'logic_name': 'RNAcentral',  # required by Genoverse
                'biotype': biotype,  # required by Genoverse
                'description': description,
                'seq_region_name': chromosome,
                'strand': coordinates['strand'],
                'start': coordinates['start'],
                'end': coordinates['end'],
                'databases': databases
            }

            upi2data[upi] = transcript
            data.append(transcript)

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

    return data


def features_from_mappings(species, chromosome, start, end):
    taxid = _species2taxid(species)
    mappings = GenomeMapping.objects.filter(taxid=taxid, chromosome=chromosome, start__gte=start, stop__lte=end)\
                                    .select_related('upi').prefetch_related('upi__precomputed')

    transcripts_query = '''
        SELECT 1 id, region_id, strand, chromosome, start, stop, mapping.taxid as taxid,
          precomputed.rna_type as rna_type, precomputed.description as description, rna.upi as upi
        FROM (
          SELECT region_id, upi, strand, chromosome, taxid, MIN(start) as start, MAX(stop) as stop
          FROM {genome_mapping}
          GROUP BY region_id, upi, strand, chromosome, taxid
          HAVING MIN(start) > {start}
             AND MAX(stop) < {stop}
             AND taxid = {taxid}
             AND chromosome = '{chromosome}'
        ) mapping
        JOIN rna
        ON mapping.upi=rna.upi
        JOIN (
          SELECT * FROM {rna_precomputed} WHERE taxid={taxid}
        ) precomputed
        ON {rna}.upi=precomputed.upi
    '''.format(
        genome_mapping=GenomeMapping._meta.db_table,
        rna=Rna._meta.db_table,
        rna_precomputed=RnaPrecomputed._meta.db_table,
        taxid=taxid,
        start=start,
        stop=end,
        chromosome=chromosome
    )

    try:
        transcripts = GenomeMapping.objects.raw(transcripts_query)
    except GenomeMapping.DoesNotExist:
        transcripts = []

    data = []
    for transcript in transcripts:
        xrefs = Xref.default_objects.filter(upi=transcript.upi.upi, taxid=taxid, deleted='N').select_related('db').all()
        databases = list(set([xref.db.display_name for xref in xrefs]))
        databases.sort()

        data.append({
            'ID': transcript.region_id,
            'external_name': transcript.upi.upi,
            'taxid': transcript.taxid,
            'feature_type': 'transcript',
            'logic_name': 'RNAcentral',
            'biotype': transcript.rna_type,
            'description': transcript.description,
            'seq_region_name': transcript.chromosome,
            'strand': transcript.strand,
            'start': transcript.start,
            'end': transcript.stop,
            'databases': databases
        })

    for i, exon in enumerate(mappings):
        try:
            biotype = exon.upi.precomputed.get(taxid=taxid).rna_type
        except exon.DoesNotExist:
            biotype = exon.upi.precomputed.get(taxid__isnull=True).rna_type

        exon_id = '_'.join([exon.region_id, 'exon_' + str(i)])
        data.append({
            'external_name': exon.region_id,
            'ID': exon_id,
            'taxid': exon.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
            'feature_type': 'exon',
            'Parent': exon.region_id,
            'logic_name': 'RNAcentral',  # required by Genoverse
            'biotype': biotype,  # required by Genoverse
            'seq_region_name': exon.chromosome,
            'strand': exon.strand,
            'start': exon.start,
            'end': exon.stop,
        })

    return data


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
        xrefs = rna.get_xrefs(taxid=taxid).filter(deleted='N')
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
    """
    List of distinct genomic locations, where a specific RNA
    was computationally mapped onto a specific genome location.

    [API documentation](/api)
    """
    queryset = Rna.objects.select_related().all()

    def get(self, request, pk=None, taxid=None, format=None):
        rna = self.get_object()
        mappings = rna.genome_mappings.filter(taxid=taxid)\
                                      .values('region_id', 'strand', 'chromosome', 'taxid', 'identity')\
                                      .annotate(Min('start'), Max('stop'))

        try:
            assembly = EnsemblAssembly.objects.get(taxid=taxid)  # this applies only to species-specific pages
        except EnsemblAssembly.DoesNotExist:
            return Response([])

        output = []
        for mapping in mappings:
            data = {
                'chromosome': mapping["chromosome"],
                'strand': mapping["strand"],
                'start': mapping["start__min"],
                'end': mapping["stop__max"],
                'identity': mapping["identity"],
                'species': assembly.ensembl_url,
                'ucsc_db_id': assembly.assembly_ucsc,
                'ensembl_division': assembly.division,
                'ensembl_species_url': assembly.ensembl_url
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


class GenomesAPIViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """API endpoint, presenting all E! assemblies, available in RNAcentral."""
    permission_classes = (AllowAny, )
    serializer_class = EnsemblAssemblySerializer
    pagination_class = Pagination
    # queryset = EnsemblAssembly.objects.prefetch_related('genome_mappings').all().order_by('-ensembl_url')
    lookup_field = 'ensembl_url'

    def get_queryset(self):
        query = '''
            SELECT 1 as id, {ensembl_assembly}.assembly_id, assembly_full_name, gca_accession, assembly_ucsc,
              common_name, taxid, ensembl_url, division, subdomain,
              example_chromosome, example_start, example_end,
              start, stop, chromosome
            FROM {ensembl_assembly}
            JOIN (
              SELECT DISTINCT ON ({genome_mapping}.assembly_id)
                {genome_mapping}.assembly_id, {genome_mapping}.start, {genome_mapping}.stop, {genome_mapping}.chromosome
              FROM {genome_mapping}
            ) mapping
            ON mapping.assembly_id = {ensembl_assembly}.assembly_id
            ORDER BY {ensembl_assembly}.ensembl_url ASC
        '''.format(
            genome_mapping=GenomeMapping._meta.db_table,
            ensembl_assembly=EnsemblAssembly._meta.db_table
        )

        # this won't really paginate
        return list(EnsemblAssembly.objects.raw(query))


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
