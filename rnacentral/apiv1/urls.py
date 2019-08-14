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

from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns
from apiv1 import views


CACHE_TIMEOUT = 60 * 60 * 24 * 1  # per-view cache timeout in seconds


urlpatterns = [
    # api root
    url(r'^$', cache_page(CACHE_TIMEOUT)(views.APIRoot.as_view()), name='api-v1-root'),
    # list of all RNAcentral entries
    url(r'^rna/?$', cache_page(CACHE_TIMEOUT)(views.RnaSequences.as_view()), name='rna-sequences'),
    # single RNAcentral sequence
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/?$', cache_page(CACHE_TIMEOUT)(views.RnaDetail.as_view()), name='rna-detail'),
    # view for all cross-references associated with an RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/?$', cache_page(CACHE_TIMEOUT)(views.XrefList.as_view()), name='rna-xrefs'),
    # view for all cross-references, filtered down to a specific taxon
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.XrefsSpeciesSpecificList.as_view()), name='rna-xrefs-species-specific'),
    # secondary structure for a species-specific entry
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/2d/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.SecondaryStructureSpeciesSpecificList.as_view()), name='rna-2d-species-specific'),
    # svg image for a species-specific entry
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/svg/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.SecondaryStructureSVGImage.as_view()), name='rna-svg-species-specific'),
    # rfam hits found in this RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/rfam-hits(/(?P<taxid>\d+))?/?$', cache_page(CACHE_TIMEOUT)(views.RfamHitsAPIViewSet.as_view()), name='rna-rfam-hits'),
    # sequence features found in a sequence (CRS, mature miRNA products etc)
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/sequence-features/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.SequenceFeaturesAPIViewSet.as_view()), name='rna-sequence-features'),
    # related sequences according to Ensembl Compara
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/ensembl-compara/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.EnsemblComparaAPIViewSet.as_view()), name='rna-ensembl-compara'),
    # all literature citations associated with an RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/publications/?$', cache_page(CACHE_TIMEOUT)(views.RnaPublicationsView.as_view()), name='rna-publications'),
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/publications/(?P<taxid>\d+)/?$',cache_page(CACHE_TIMEOUT)(views.RnaPublicationsView.as_view()), name='rna-publications'),
    # species-specific RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})(/|_)(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.RnaSpeciesSpecificView.as_view()), name='rna-species-specific'),
    # genome locations for RNA (species-specific)
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/genome-locations/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.RnaGenomeLocations.as_view()), name='rna-genome-locations'),
    # go annotations for RNA (species-specific)
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/go-annotations/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.RnaGoAnnotationsView.as_view()), name='rna-go-annotations'),
    # target proteins for RNA (species-specific)
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/protein-targets/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.ProteinTargetsView.as_view()), name='rna-protein-targets'),
    # target lncRNA for RNA (species-specific)
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/lncrna-targets/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.LncrnaTargetsView.as_view()), name='rna-lncrna-targets'),
    # literature citations associated with ENA records
    url(r'^accession/(?P<pk>.*?)/citations/?$', cache_page(CACHE_TIMEOUT)(views.CitationsView.as_view()), name='accession-citations'),
    # view for an individual cross-reference
    url(r'^accession/(?P<pk>.*?)/info/?$', cache_page(CACHE_TIMEOUT)(views.AccessionView.as_view()), name='accession-detail'),
    # Ensembl-like genome coordinates endpoint
    url(r'^(feature|overlap)/region/(?P<species>\w+)/(?P<chromosome>[\w\.]+)\:(?P<start>(\d|,)+)-(?P<end>(\d|,)+)/?$',
        cache_page(CACHE_TIMEOUT)(views.GenomeAnnotations.as_view()), name='human-genome-coordinates'),
    # expert databases as stored in config dict
    url(r'^expert-dbs/$', views.ExpertDatabasesAPIView.as_view(), {}, name='expert-dbs-api'),
    # expert databases stats
    url(r'^expert-db-stats/$', views.ExpertDatabasesStatsViewSet.as_view({'get': 'list'}), {}, name='expert-db-stats'),
    url(r'^expert-db-stats/(?P<pk>.*)/?$', views.ExpertDatabasesStatsViewSet.as_view({'get': 'retrieve'}), {}, name='expert-db-stats'),
    # genomes - ensembl assemblies list
    url(r'genomes/$', cache_page(CACHE_TIMEOUT)(views.GenomesAPIViewSet.as_view({'get': 'list'})), {}, name='genomes-api'),
    # mapping of ensembl assemblies to insdc submissions
    url(r'ensembl-insdc-mapping/$', views.EnsemblInsdcMappingView.as_view(), {}, name='ensembl-insdc-mapping'),
    # endpoint that returns karyotypes, downloaded from ensembl
    url(r'karyotypes/(?P<ensembl_url>.*?)/?$', cache_page(CACHE_TIMEOUT)(views.EnsemblKaryotypeAPIView.as_view()), {}, name='ensembl-karyotype'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'yaml', 'fasta', 'api', 'gff', 'gff3', 'bed'])
