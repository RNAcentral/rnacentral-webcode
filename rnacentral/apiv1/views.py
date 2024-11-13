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
import json
import re
import zlib
from itertools import chain

import boto3
import requests
from apiv1.renderers import RnaFastaRenderer
from apiv1.serializers import (
    AccessionSerializer,
    CitationSerializer,
    EnsemblAssemblySerializer,
    EnsemblComparaSerializer,
    ExpertDatabaseStatsSerializer,
    InteractionsSerializer,
    LitSummSerializer,
    LncrnaTargetsSerializer,
    Md5Serializer,
    ProteinTargetsSerializer,
    QcStatusSerializer,
    RawPublicationSerializer,
    RfamHitSerializer,
    RnaFastaSerializer,
    RnaFlatSerializer,
    RnaGenomeLocationsSerializer,
    RnaNestedSerializer,
    RnaSecondaryStructureSerializer,
    RnaSpeciesSpecificSerializer,
    SequenceFeatureSerializer,
    XrefSerializer,
)
from colorhash import ColorHash
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from portal.config.expert_databases import expert_dbs
from portal.models import (
    Accession,
    AccessionSequenceRegion,
    Database,
    DatabaseStats,
    EnsemblAssembly,
    EnsemblCompara,
    GoAnnotation,
    Interactions,
    LitSumm,
    ProteinInfo,
    QcStatus,
    RelatedSequence,
    RfamHit,
    Rna,
    RnaPrecomputed,
    SequenceFeature,
    SequenceRegion,
    SequenceRegionActive,
    Taxonomy,
)
from rest_framework import generics, renderers, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework_yaml.renderers import YAMLRenderer

from rnacentral.utils.pagination import LargeTablePagination, Pagination

"""
Docstrings of the classes exposed in urlpatterns support markdown.
"""

# maximum number of xrefs to use with prefetch_related
MAX_XREFS_TO_PREFETCH = 1000


def get_database(region):
    # get databases from rnc_accession_sequence_region table
    databases = []
    for item in AccessionSequenceRegion.objects.filter(
        region_id=region.id
    ).select_related("accession"):
        databases.append(item.accession.database)

    # use display_name from rnc_database
    providing_databases = []
    for item in databases:
        try:
            providing_databases.append(Database.objects.get(descr=item).display_name)
        except Database.DoesNotExist:
            pass

    return providing_databases


class GenomeAnnotations(APIView):
    """
    Ensembl-like genome coordinates endpoint.

    [API documentation](/api)
    """

    # the above docstring appears on the API website

    permission_classes = (AllowAny,)

    def get(self, request, species, chromosome, start, end, format=None):
        start = start.replace(",", "")
        end = end.replace(",", "")

        try:
            assembly = EnsemblAssembly.objects.filter(ensembl_url=species).first()
        except EnsemblAssembly.DoesNotExist:
            return Response([])

        regions = (
            SequenceRegion.objects.select_related("urs_taxid")
            .prefetch_related("exons")
            .filter(
                assembly=assembly,
                chromosome=chromosome,
                region_start__gte=start,
                region_stop__lte=end,
                urs_taxid__is_active=True,
            )
        )

        features = []
        for transcript in regions:
            providing_databases = get_database(transcript)
            features.append(
                {
                    "ID": transcript.region_name,
                    "external_name": transcript.urs_taxid.id.split("_")[0],
                    "taxid": assembly.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                    "feature_type": "transcript",
                    "logic_name": "RNAcentral",  # required by Genoverse
                    "biotype": transcript.urs_taxid.rna_type,  # required by Genoverse
                    "description": transcript.urs_taxid.short_description,
                    "seq_region_name": transcript.chromosome,
                    "strand": transcript.strand,
                    "start": transcript.region_start,
                    "end": transcript.region_stop,
                    "databases": providing_databases,
                }
            )

            # exons
            for exon in transcript.exons.all():
                features.append(
                    {
                        "external_name": exon.id,
                        "ID": exon.id,
                        "taxid": assembly.taxid,  # added by Burkov for generating links to E! in Genoverse populateMenu() popups
                        "feature_type": "exon",
                        "Parent": transcript.region_name,
                        "logic_name": "RNAcentral",  # required by Genoverse
                        "biotype": transcript.urs_taxid.rna_type,  # required by Genoverse
                        "seq_region_name": transcript.chromosome,
                        "strand": transcript.strand,
                        "start": exon.exon_start,
                        "end": exon.exon_stop,
                    }
                )

        return Response(features)

from django.urls import NoReverseMatch

def build_feature_url(request, species, chromosome, start, end):
    """

    Builds the URL for the feature endpoint based on the provided parameters.
    This function is a workaround for the reverse() function, which cannot find a compatible regex
    due to the presence of colons in the pattern.

    Parameters:
    - request: The Django request object.
    - species: The species for which the feature URL is being generated.
    - chromosome: The chromosome number or name for the feature.
    - start: The start position of the feature.
    - end: The end position of the feature.

    Returns:
    - A string representing the absolute URL of the feature endpoint.
    """
    base = '/api/v1/feature/region'
    path = f"{base}/{species}/{chromosome}:{start}-{end}"
    return request.build_absolute_uri(path)


class APIRoot(APIView):
    """
    This is the root of the RNAcentral API Version 1.

    [API documentation](/api)
    """

    # the above docstring appears on the API website
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        endpoints = {
            'rna': 'rna-sequences',
            'accession': ('accession-detail', {'pk': 'URS000075D2D3'}),
            'accession_citations': ('accession-citations', {'pk': 'URS000075D2D3'}),
            #'feature': ('human-genome-coordinates', {'species': 'homo_sapiens', 
            #                          'chromosome': 'Y', 'start': 1, 'end': 1000000}),
            # The above does not work because reverse() cannot find a compatible regex
            # See build_feature_url()
            
            'expert-db-stats': 'expert-db-stats',
            'genomes': 'genomes-api',
            'genome-browser': ('genome-browser-api', {'species': 'human'}),
            'litsumm': 'litsumm',
            'md5': ('md5-sequence', {'md5': '6bba097c8c39ed9a0fdf02273ee1c79a'}),
        }

        result = {}

        result['feature'] = build_feature_url(
            request, 
            species='human',
            chromosome='Y',
            start='1',
            end='1000000'
        )

        for key, value in endpoints.items():
            # Debuggin implementation to make sure reverse() works
            try:
                if isinstance(value, tuple):
                    result[key] = reverse(value[0], request=request, format=format, kwargs=value[1])
                else:
                    result[key] = reverse(value, request=request, format=format)
            except NoReverseMatch as e:
                # Skip this endpoint if it can't be reversed
                pass

        return Response(result)


class RnaFilter(filters.FilterSet):
    """Declare what fields can be filtered using django-filters"""

    min_length = filters.NumberFilter(field_name="length", lookup_expr="gte")
    max_length = filters.NumberFilter(field_name="length", lookup_expr="lte")
    external_id = filters.CharFilter(
        field_name="xrefs__accession__external_id", distinct=True
    )

    class Meta:
        model = Rna
        fields = ["upi", "md5", "length", "min_length", "max_length", "external_id"]


class RnaMixin(object):
    """Mixin for additional functionality specific to Rna views."""

    def get_serializer_class(self):
        """Determine a serializer for RnaSequences and RnaDetail views."""
        if self.request.accepted_renderer.format == "fasta":
            return RnaFastaSerializer

        flat = self.request.query_params.get("flat", "false")
        if re.match("true", flat, re.IGNORECASE):
            return RnaFlatSerializer
        return RnaNestedSerializer


class RnaSequences(RnaMixin, generics.ListAPIView):
    """
    Unique RNAcentral Sequences

    [API documentation](/api)
    """

    # the above docstring appears on the API website
    permission_classes = (AllowAny,)
    filterset_class = RnaFilter
    renderer_classes = (
        renderers.JSONRenderer,
        JSONPRenderer,
        renderers.BrowsableAPIRenderer,
        YAMLRenderer,
        RnaFastaRenderer,
    )
    pagination_class = LargeTablePagination

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
        flat = self.request.query_params.get("flat", None)
        if flat:
            to_prefetch = []
            no_prefetch = []
            for rna in page:
                if rna.xrefs.count() <= MAX_XREFS_TO_PREFETCH:
                    to_prefetch.append(rna.upi)
                else:
                    no_prefetch.append(rna.upi)

            prefetched = self.filter_queryset(
                Rna.objects.filter(upi__in=to_prefetch)
                .prefetch_related("xrefs__accession")
                .all()
            )
            not_prefetched = self.filter_queryset(
                Rna.objects.filter(upi__in=no_prefetch).all()
            )

            result_list = list(chain(prefetched, not_prefetched))
            page = result_list  # .object_list is no longer set on the instance
        # end RNAcentral override

        # begin DRF base code
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        # end DRF base code

    def get_queryset(self):
        """
        The `database` query parameter filter has been removed to prevent queries,
        most likely made by crawlers, from overloading the service
        """
        # `seq_long` **must** be deferred in order for filters to work
        queryset = Rna.objects.defer("seq_long")
        return queryset.all()


class RnaDetail(RnaMixin, generics.RetrieveAPIView):
    """
    Unique RNAcentral Sequence

    [API documentation](/api)
    """

    # the above docstring appears on the API website
    queryset = Rna.objects.all()
    renderer_classes = (
        renderers.JSONRenderer,
        JSONPRenderer,
        renderers.BrowsableAPIRenderer,
        YAMLRenderer,
        RnaFastaRenderer,
    )

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

        flat = self.request.query_params.get("flat", None)
        if flat and rna.xrefs.count() <= MAX_XREFS_TO_PREFETCH:
            queryset = queryset.prefetch_related("xrefs", "xrefs__accession")
            return get_object_or_404(queryset, **filter_kwargs)
        else:
            return rna


class RnaSpeciesSpecificView(APIView):
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
    queryset = RnaPrecomputed.objects.all()

    def get_object(self, pk):
        try:
            return RnaPrecomputed.objects.get(pk=pk)
        except RnaPrecomputed.DoesNotExist:
            raise Http404

    def get(self, request, pk, taxid, format=None):
        urs = pk + "_" + taxid
        rna = self.get_object(urs)

        # queries on the xref table make the API very slow.
        # get gene from Search Index
        search_index = settings.EBI_SEARCH_ENDPOINT
        try:
            response = requests.get(
                f"{search_index}/entry/{urs}?format=json&fields=gene"
            )
            data = json.loads(response.text)
            gene = data["entries"][0]["fields"]["gene"]
        except Exception:
            gene = ""

        try:
            species = Taxonomy.objects.get(id=taxid).name
        except Taxonomy.DoesNotExist:
            species = ""

        # LitScan data - get related IDs
        pub_list = [urs]
        query_jobs = (
            f'?query=entry_type:metadata%20AND%20primary_id:"{urs}"%20AND%20database:rnacentral&'
            f"fields=job_id&format=json"
        )
        try:
            response = requests.get(search_index + "-litscan" + query_jobs).json()
            entries = response["entries"]
            for entry in entries:
                pub_list.append(entry["fields"]["job_id"][0])
        except (IndexError, KeyError):
            pass

        # get number of articles identified by LitScan
        query_ids = ['job_id:"' + item + '"' for item in pub_list]
        query_ids = "%20OR%20".join(query_ids)
        query = f"?query=entry_type:Publication%20AND%20({query_ids})&format=json"
        try:
            response = requests.get(search_index + "-litscan" + query).json()
            pub_count = response["hitCount"]
        except KeyError:
            pub_count = None

        serializer = RnaSpeciesSpecificSerializer(
            rna,
            context={
                "gene": gene,
                "pub_count": pub_count,
                "request": request,
                "species": species,
                "taxid": taxid,
            },
        )
        return Response(serializer.data)


class XrefList(generics.ListAPIView):
    """
    List of cross-references for a particular RNA sequence.

    [API documentation](/api)
    """

    serializer_class = XrefSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs["pk"]
        return Rna.objects.get(upi=upi).get_xrefs()


class XrefsSpeciesSpecificList(generics.ListAPIView):
    """
    List of cross-references for a particular RNA sequence in a specific species.

    [API documentation](/api)
    """

    serializer_class = XrefSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs["pk"]
        taxid = self.kwargs["taxid"]
        return Rna.objects.get(upi=upi).get_xrefs(taxid=taxid)


class SecondaryStructureSpeciesSpecificList(generics.ListAPIView):
    """
    List of secondary structures for a particular RNA sequence in a specific species.

    [API documentation](/api)
    """

    queryset = Rna.objects.all()

    def get(self, request, pk=None, taxid=None, format=None):
        """Get a list of secondary structures"""
        rna = self.get_object()
        serializer = RnaSecondaryStructureSerializer(rna)
        return Response(serializer.data)


class SecondaryStructureSVGImage(generics.ListAPIView):
    """
    SVG image for an RNA sequence.
    """

    permission_classes = (AllowAny,)

    def get(self, request, pk=None, format=None):
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=settings.S3_SERVER["KEY"],
            aws_secret_access_key=settings.S3_SERVER["SECRET"],
            endpoint_url=settings.S3_SERVER["HOST"],
        )

        upi = list(self.kwargs["pk"])
        upi_path = (
            "".join(upi[0:3])
            + "/"
            + "".join(upi[3:5])
            + "/"
            + "".join(upi[5:7])
            + "/"
            + "".join(upi[7:9])
            + "/"
            + "".join(upi[9:11])
            + "/"
        )

        s3_file = "prod/" + upi_path + self.kwargs["pk"] + ".svg.gz"
        s3_obj = s3.Object(settings.S3_SERVER["BUCKET"], s3_file)
        try:
            s3_svg = zlib.decompress(s3_obj.get()["Body"].read(), zlib.MAX_WBITS | 32)
        except s3.meta.client.exceptions.NoSuchKey:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(
            self.generate_thumbnail(s3_svg.decode("utf-8"), "".join(upi)),
            content_type="image/svg+xml",
        )

    def generate_thumbnail(self, image, upi):
        move_to_start_position = None
        color = ColorHash(upi).hex
        points = []
        width = []
        height = []
        for i, line in enumerate(image.split("\n")):
            if not width:
                width = re.findall(r'width="(\d+(\.\d+)?)"', line)
            if not height:
                height = re.findall(r'height="(\d+(\.\d+)?)"', line)
            for nt in re.finditer(
                '<text x="(\d+)(\.\d+)?" y="(\d+)(\.\d+)?".*?</text>', line
            ):
                if "numbering-label" in nt.group(0):
                    continue
                if not move_to_start_position:
                    move_to_start_position = "M{} {} ".format(nt.group(1), nt.group(3))
                points.append("L{} {}".format(nt.group(1), nt.group(3)))
        if len(points) < 200:
            stroke_width = "3"
        elif len(points) < 500:
            stroke_width = "4"
        elif len(points) < 3000:
            stroke_width = "4"
        else:
            stroke_width = "2"
        thumbnail = '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}"><path style="stroke:{};stroke-width:{}px;fill:none;" d="'.format(
            width[0][0], height[0][0], color, stroke_width
        )
        thumbnail += move_to_start_position
        thumbnail += " ".join(points)
        thumbnail += '"/></svg>'
        return thumbnail


class RnaGenomeLocations(generics.ListAPIView):
    """
    List of distinct genomic locations, where a specific RNA
    is found in a specific species, extracted from xrefs.

    [API documentation](/api)
    """

    serializer_class = RnaGenomeLocationsSerializer

    def get_queryset(self):
        urs_taxid = self.kwargs["pk"] + "_" + self.kwargs["taxid"]

        # do not show genome coordinates for obsolete sequences
        try:
            rna_precomputed = RnaPrecomputed.objects.get(id=urs_taxid, is_active=True)
        except RnaPrecomputed.DoesNotExist:
            return SequenceRegionActive.objects.none()

        sequence_region_active_query = """
            SELECT
                {sequence_region_active}.id,
                {sequence_region_active}.chromosome,
                {sequence_region_active}.strand,
                {sequence_region_active}.region_start,
                {sequence_region_active}.region_stop,
                {sequence_region_active}.identity,
                {ensembl_assembly}.assembly_id,
                {ensembl_assembly}.assembly_full_name,
                {ensembl_assembly}.gca_accession,
                {ensembl_assembly}.assembly_ucsc,
                {ensembl_assembly}.taxid,
                {ensembl_assembly}.ensembl_url,
                {ensembl_assembly}.division,
                {ensembl_assembly}.subdomain,
                {ensembl_assembly}.example_chromosome,
                {ensembl_assembly}.example_start,
                {ensembl_assembly}.example_end,
                {taxonomy}.name as common_name
            FROM {sequence_region_active}
            LEFT JOIN {ensembl_assembly}
            ON {ensembl_assembly}.assembly_id = {sequence_region_active}.assembly_id
            LEFT JOIN {taxonomy}
            ON {taxonomy}.id = {ensembl_assembly}.taxid
            WHERE {sequence_region_active}.urs_taxid = '{rna_precomputed}'
            ORDER BY {ensembl_assembly}.assembly_id
        """.format(
            sequence_region_active=SequenceRegionActive._meta.db_table,
            ensembl_assembly=EnsemblAssembly._meta.db_table,
            taxonomy=Taxonomy._meta.db_table,
            rna_precomputed=rna_precomputed,
        )

        return SequenceRegionActive.objects.raw(sequence_region_active_query)


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
        pk = self.kwargs["pk"]
        return Accession.objects.select_related().get(pk=pk).refs.all()


class RnaPublicationsView(generics.ListAPIView):
    """
    API endpoint that allows the citations associated with
    each Unique RNA Sequence to be viewed.

    [API documentation](/api)
    """

    # the above docstring appears on the API website
    permission_classes = (AllowAny,)
    serializer_class = RawPublicationSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs["pk"]
        taxid = self.kwargs["taxid"] if "taxid" in self.kwargs else None
        return Rna.objects.get(upi=upi).get_publications(
            taxid
        )  # this is actually a list


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
            if re.match("tmrna-website", expert_db_label, flags=re.IGNORECASE):
                expert_db_label = "TMRNA_WEB"
            else:
                expert_db_label = expert_db_label.upper()
            return expert_db_label

        # e.g. { "TMRNA_WEB": {'name': 'tmRNA Website', 'label': 'tmrna-website', ...}}
        databases = {db["descr"]: db for db in Database.objects.values()}

        # update config.expert_databases json with Database table objects
        for db in expert_dbs:
            normalized_label = _normalize_expert_db_label(db["label"])
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
    lookup_field = "pk"

    def list(self, request, *args, **kwargs):
        return super(ExpertDatabasesStatsViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(ExpertDatabasesStatsViewSet, self).retrieve(
            request, *args, **kwargs
        )


class GenomesAPIViewSet(ListModelMixin, GenericViewSet):
    """API endpoint, presenting all E! assemblies, available in RNAcentral."""

    permission_classes = (AllowAny,)
    serializer_class = EnsemblAssemblySerializer
    pagination_class = Pagination
    lookup_field = "ensembl_url"

    def get_queryset(self):
        ensembl_assembly_query = """
            SELECT
                {ensembl_assembly}.assembly_id,
                {ensembl_assembly}.assembly_full_name,
                {ensembl_assembly}.gca_accession,
                {ensembl_assembly}.assembly_ucsc,
                {ensembl_assembly}.taxid,
                {ensembl_assembly}.ensembl_url,
                {ensembl_assembly}.division,
                {ensembl_assembly}.subdomain,
                {ensembl_assembly}.example_chromosome,
                {ensembl_assembly}.example_start,
                {ensembl_assembly}.example_end,
                {taxonomy}.name as common_name
            FROM {ensembl_assembly}
            LEFT JOIN {taxonomy}
            ON {taxonomy}.id = {ensembl_assembly}.taxid
            ORDER BY {taxonomy}.name
        """.format(
            ensembl_assembly=EnsemblAssembly._meta.db_table,
            taxonomy=Taxonomy._meta.db_table,
        )

        queryset = EnsemblAssembly.objects.raw(ensembl_assembly_query)
        return queryset


class RfamHitsAPIViewSet(generics.ListAPIView):
    """API endpoint with Rfam models that are found in an RNA."""

    permission_classes = (AllowAny,)
    serializer_class = RfamHitSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs["pk"]
        return (
            RfamHit.objects.filter(upi=upi)
            .select_related("rfam_model")
            .select_related("upi")
        )

    def get_serializer_context(self):
        return {"taxid": self.kwargs["taxid"]} if "taxid" in self.kwargs else {}


class SequenceFeaturesAPIViewSet(generics.ListAPIView):
    """API endpoint with sequence features (CRS, mature miRNAs etc)"""

    permission_classes = (AllowAny,)
    serializer_class = SequenceFeatureSerializer
    pagination_class = Pagination

    def get_queryset(self):
        upi = self.kwargs["pk"]
        taxid = self.kwargs["taxid"]
        features = SequenceFeature.objects.filter(
            upi=upi, taxid=taxid, stop__gt=0
        ).exclude(feature_name__in=["modification", "rfam_hit"])

        # some features have duplicate data
        features_list = [
            "anticodon",
            "tmrna_ivs",
            "tmrna_acceptor",
            "tmrna_tagcds",
            "tmrna_exon",
            "tmrna_gpi",
            "tmrna_body",
            "tmrna_ccaequiv",
            "tmrna_coding_region",
        ]
        distinct_features = features.filter(feature_name__in=features_list).distinct(
            "feature_name"
        )
        remove_features = features.exclude(feature_name__in=features_list)

        return remove_features.union(distinct_features).order_by(
            "feature_name", "start"
        )


class RnaGoAnnotationsView(APIView):
    permission_classes = (AllowAny,)
    pagination_class = Pagination

    def get(self, request, pk, taxid, **kwargs):
        rna_id = pk + "_" + taxid
        taxid = int(taxid)
        annotations = GoAnnotation.objects.filter(rna_id=rna_id).select_related(
            "ontology_term", "evidence_code"
        )

        result = []
        for annotation in annotations:
            result.append(
                {
                    "rna_id": annotation.rna_id,
                    "upi": pk,
                    "taxid": taxid,
                    "go_term_id": annotation.ontology_term.ontology_term_id,
                    "go_term_name": annotation.ontology_term.name,
                    "qualifier": annotation.qualifier,
                    "evidence_code_id": annotation.evidence_code.ontology_term_id,
                    "evidence_code_name": annotation.evidence_code.name,
                    "assigned_by": annotation.assigned_by,
                    "extensions": annotation.assigned_by or {},
                }
            )

        return Response(result)


class ProteinTargetsView(generics.ListAPIView):
    """API endpoint, presenting ProteinInfo, related to given rna."""

    permission_classes = ()
    authentication_classes = ()
    pagination_class = Pagination
    serializer_class = ProteinTargetsSerializer

    def get_queryset(self):
        pk = self.kwargs["pk"]
        taxid = self.kwargs["taxid"]

        # we select redundant {protein_info}.protein_accession because
        # otherwise django curses about lack of primary key in raw query
        protein_info_query = """
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
        """.format(
            rna=Rna._meta.db_table,
            rna_precomputed=RnaPrecomputed._meta.db_table,
            related_sequence=RelatedSequence._meta.db_table,
            protein_info=ProteinInfo._meta.db_table,
            pk=pk,
            taxid=taxid,
        )

        # queryset = PaginatedRawQuerySet(protein_info_query, model=ProteinInfo)  # was: ProteinInfo.objects.raw(protein_info_query)
        queryset = ProteinInfo.objects.raw(protein_info_query)
        return queryset


class LncrnaTargetsView(generics.ListAPIView):
    """API endpoint, presenting lncRNAs targeted by a given rna."""

    permission_classes = ()
    authentication_classes = ()
    pagination_class = Pagination
    serializer_class = LncrnaTargetsSerializer

    def get_queryset(self):
        pk = self.kwargs["pk"]
        taxid = self.kwargs["taxid"]

        # we select redundant {protein_info}.protein_accession because
        # otherwise django curses about lack of primary key in raw query
        protein_info_query = """
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
        """.format(
            rna_precomputed=RnaPrecomputed._meta.db_table,
            related_sequence=RelatedSequence._meta.db_table,
            protein_info=ProteinInfo._meta.db_table,
            pk=pk,
            taxid=taxid,
        )
        # queryset = PaginatedRawQuerySet(protein_info_query, model=ProteinInfo)
        queryset = ProteinInfo.objects.raw(protein_info_query)
        return queryset


class QcStatusView(APIView):
    """API endpoint showing the QC status for a sequence"""

    permission_classes = ()
    authentication_classes = ()

    def get(self, _request, pk, taxid):
        urs_taxid = f"{pk}_{taxid}"
        status = QcStatus.objects.get(id=urs_taxid)
        serializer = QcStatusSerializer(status)
        return Response(serializer.data)


class LargerPagination(Pagination):
    page_size = 50
    ensembl_compara_url = None
    compara_status = None

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
                "ensembl_compara_url": self.ensembl_compara_url,
                "ensembl_compara_status": self.ensembl_compara_status,
            }
        )


class EnsemblComparaAPIViewSet(generics.ListAPIView):
    """API endpoint for related sequences identified by Ensembl Compara"""

    permission_classes = (AllowAny,)
    serializer_class = EnsemblComparaSerializer
    pagination_class = LargerPagination
    ensembl_transcript_id = ""

    def get_queryset(self):
        upi = self.kwargs["pk"]
        taxid = self.kwargs["taxid"]
        self_urs_taxid = upi + "_" + taxid
        urs_taxid = EnsemblCompara.objects.filter(urs_taxid__id=self_urs_taxid).first()
        if urs_taxid:
            self.ensembl_transcript_id = urs_taxid.ensembl_transcript_id
            return (
                EnsemblCompara.objects.filter(homology_id=urs_taxid.homology_id)
                .exclude(urs_taxid=self_urs_taxid)
                .order_by("urs_taxid__description")
                .all()
            )
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

        return Response({"data": serializer.data})

    def get_ensembl_compara_url(self):
        urs_taxid = self.kwargs["pk"] + "_" + self.kwargs["taxid"]
        genome_region = SequenceRegion.objects.filter(urs_taxid__id=urs_taxid).first()
        if genome_region and self.ensembl_transcript_id:
            return (
                "http://www.ensembl.org/"
                + genome_region.assembly.ensembl_url
                + "/Gene/Compara_Tree?t="
                + self.ensembl_transcript_id
            )
        else:
            return None

    def get_ensembl_compara_status(self):
        urs_taxid = self.kwargs["pk"] + "_" + self.kwargs["taxid"]

        rna_precomputed = RnaPrecomputed.objects.get(id=urs_taxid)
        if rna_precomputed.databases and "Ensembl" not in rna_precomputed.databases:
            return "analysis not available"

        compara = EnsemblCompara.objects.filter(urs_taxid=urs_taxid).first()
        if compara:
            compara_count = EnsemblCompara.objects.filter(
                homology_id=compara.homology_id
            ).count()

        if not compara or compara_count == 0:
            return "RNA type not supported"

        if compara_count == 1:
            return "not found"

        return "found"


class InteractionsView(generics.ListAPIView):
    """API endpoint for interactions."""

    serializer_class = InteractionsSerializer

    def get_queryset(self):
        urs_taxid = self.kwargs["pk"] + "_" + self.kwargs["taxid"]
        return (
            Interactions.objects.filter(urs_taxid=urs_taxid)
            .distinct("interacting_id")
            .exclude(interacting_id__contains="mgi")
        )


class GenomeBrowserAPIViewSet(APIView):
    """Render genome-browser, taking into account start/end locations."""

    permission_classes = (AllowAny,)

    def get(self, request, species, format=None):
        assembly = EnsemblAssembly.objects.filter(ensembl_url=species).first()
        if assembly is None:
            return Response([])

        region = (
            SequenceRegionActive.objects.filter(assembly_id=assembly.assembly_id)
            .order_by("chromosome")
            .first()
        )

        if region is None:
            return Response([])

        chromosome = (
            assembly.example_chromosome
            if assembly.example_chromosome
            else region.chromosome
        )
        start = (
            assembly.example_start if assembly.example_start else region.region_start
        )
        end = assembly.example_end if assembly.example_end else region.region_stop
        common_name = (
            assembly.common_name.title()
            if assembly.common_name
            else assembly.ensembl_url.replace("_", " ").title()
        )

        return Response(
            {
                "assembly_id": assembly.assembly_id,
                "common_name": common_name,
                "chromosome": chromosome,
                "start": start,
                "end": end,
                "ensembl_url": assembly.ensembl_url,
            }
        )


class LitSummView(ReadOnlyModelViewSet):
    """API endpoint to show LitSumm summaries"""

    serializer_class = LitSummSerializer
    lookup_field = "rna_id"

    def get_queryset(self):
        """
        Optionally restricts the returned summaries to a given URS,
        by filtering against a `URS` query parameter in the URL.
        """
        queryset = LitSumm.objects.all()
        primary_id = self.request.query_params.get("urs")
        if primary_id is not None:
            queryset = queryset.filter(primary_id=primary_id)
        return queryset


class Md5SequenceView(APIView):
    """API endpoint to fetch sequence using md5 field"""

    permission_classes = (AllowAny,)

    def get(self, request, md5):
        try:
            rna = Rna.objects.get(md5=md5)
        except Rna.DoesNotExist:
            raise Http404

        precomputed = RnaPrecomputed.objects.filter(upi=rna, taxid__isnull=True).first()
        if not precomputed:
            raise Http404

        serializer = Md5Serializer(precomputed)
        return Response(serializer.data)
