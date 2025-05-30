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

from apiv1 import views
from django.urls import re_path
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns

CACHE_TIMEOUT = 60 * 60 * 24 * 1  # per-view cache timeout in seconds


urlpatterns = [
    # api root
    re_path(
        r"^$", cache_page(CACHE_TIMEOUT)(views.APIRoot.as_view()), name="api-v1-root"
    ),
    # list of all RNAcentral entries
    re_path(
        r"^rna/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaSequences.as_view()),
        name="rna-sequences",
    ),
    # single RNAcentral sequence
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaDetail.as_view()),
        name="rna-detail",
    ),
    # view for all cross-references associated with an RNAcentral id
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/?$",
        cache_page(CACHE_TIMEOUT)(views.XrefList.as_view()),
        name="rna-xrefs",
    ),
    # view for all cross-references, filtered down to a specific taxon
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.XrefsSpeciesSpecificList.as_view()),
        name="rna-xrefs-species-specific",
    ),
    # secondary structure for a species-specific entry
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/2d(?:/(?P<taxid>\d+))?/$",
        cache_page(CACHE_TIMEOUT)(
            views.SecondaryStructureSpeciesSpecificList.as_view()
        ),
        name="rna-2d-species-specific",
    ),
    # secondary structure thumbnail in SVG format
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/2d/svg/?$",
        cache_page(CACHE_TIMEOUT)(views.SecondaryStructureSVGImage.as_view()),
        name="rna-2d-svg",
    ),
    # rfam hits found in this RNAcentral id
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/rfam-hits/(?P<taxid>\d+)?/?$",
        cache_page(CACHE_TIMEOUT)(views.RfamHitsAPIViewSet.as_view()),
        name="rna-rfam-hits",
    ),
    # sequence features found in a sequence (CRS, mature miRNA products etc)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/sequence-features/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.SequenceFeaturesAPIViewSet.as_view()),
        name="rna-sequence-features",
    ),
    # related sequences according to Ensembl Compara
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/ensembl-compara/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.EnsemblComparaAPIViewSet.as_view()),
        name="rna-ensembl-compara",
    ),
    # all literature citations associated with an RNAcentral id
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/publications/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaPublicationsView.as_view()),
        name="rna-publications",
    ),
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/publications/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaPublicationsView.as_view()),
        name="rna-publications",
    ),
    # species-specific RNAcentral id
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})[/_](?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaSpeciesSpecificView.as_view()),
        name="rna-species-specific",
    ),
    # interactions for RNA (species-specific)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/interactions/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.InteractionsView.as_view()),
        name="interactions",
    ),
    # genome locations for RNA (species-specific)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/genome-locations/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaGenomeLocations.as_view()),
        name="rna-genome-locations",
    ),
    # go annotations for RNA (species-specific)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/go-annotations/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.RnaGoAnnotationsView.as_view()),
        name="rna-go-annotations",
    ),
    # target proteins for RNA (species-specific)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/protein-targets/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.ProteinTargetsView.as_view()),
        name="rna-protein-targets",
    ),
    # target lncRNA for RNA (species-specific)
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/lncrna-targets/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.LncrnaTargetsView.as_view()),
        name="rna-lncrna-targets",
    ),
    # Information about the qc status for a given sequence
    re_path(
        r"^rna/(?P<pk>URS[0-9A-Fa-f]{10})/qc-status/(?P<taxid>\d+)/?$",
        cache_page(CACHE_TIMEOUT)(views.QcStatusView.as_view()),
        name="qc-status",
    ),
    # literature citations associated with ENA records
    re_path(
        r"^accession/(?P<pk>.*?)/citations/?$",
        cache_page(CACHE_TIMEOUT)(views.CitationsView.as_view()),
        name="accession-citations",
    ),
    # view for an individual cross-reference
    re_path(
        r"^accession/(?P<pk>.*?)/info/?$",
        cache_page(CACHE_TIMEOUT)(views.AccessionView.as_view()),
        name="accession-detail",
    ),
    # Ensembl-like genome coordinates endpoint
    re_path(
        r"^(feature|overlap)/region/(?P<species>\w+)/(?P<chromosome>[\w\.]+)\:(?P<start>(\d|,)+)-(?P<end>(\d|,)+)/?$",
        cache_page(CACHE_TIMEOUT)(views.GenomeAnnotations.as_view()),
        name="human-genome-coordinates",
    ),
    # expert databases as stored in config dict
    re_path(
        r"^expert-dbs/$",
        views.ExpertDatabasesAPIView.as_view(),
        {},
        name="expert-dbs-api",
    ),
    # expert databases stats
    re_path(
        r"^expert-db-stats/$",
        views.ExpertDatabasesStatsViewSet.as_view({"get": "list"}),
        {},
        name="expert-db-stats",
    ),
    re_path(
        r"^expert-db-stats/(?P<pk>.*)/?$",
        views.ExpertDatabasesStatsViewSet.as_view({"get": "retrieve"}),
        {},
        name="expert-db-stats",
    ),
    # genomes - ensembl assemblies list
    re_path(
        r"genomes/$",
        cache_page(CACHE_TIMEOUT)(views.GenomesAPIViewSet.as_view({"get": "list"})),
        {},
        name="genomes-api",
    ),
    # IGV - Genome Browser
    re_path(
        r"^genome-browser/(?P<species>\w+)/?$",
        cache_page(CACHE_TIMEOUT)(views.GenomeBrowserAPIViewSet.as_view()),
        name="genome-browser-api",
    ),
    # endpoint that returns litsumm summaries
    re_path(
        r"litsumm/$",
        cache_page(CACHE_TIMEOUT)(views.LitSummView.as_view({"get": "list"})),
        {},
        name="litsumm",
    ),
    # endpoint that returns a specific litsumm summary
    re_path(
        r"litsumm/(?P<rna_id>.*?)/?$",
        cache_page(CACHE_TIMEOUT)(views.LitSummView.as_view({"get": "retrieve"})),
        {},
        name="litsumm-specific-id",
    ),
    # fetch sequence using md5
    re_path(
        r"md5/(?P<md5>.*?)/?$",
        cache_page(CACHE_TIMEOUT)(views.Md5SequenceView.as_view()),
        name="md5-sequence",
    ),
]

urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=["json", "yaml", "fasta", "api"]
)
