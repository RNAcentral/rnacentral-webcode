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

from django.conf.urls import patterns, url, include
from django.views.decorators.cache import cache_page
from rest_framework.urlpatterns import format_suffix_patterns
from apiv1 import views


CACHE_TIMEOUT = 60 * 60 * 24 * 1 # per-view cache timeout in seconds

urlpatterns = patterns('',
	# api root
	url(r'^$', cache_page(CACHE_TIMEOUT)(views.APIRoot.as_view()), name='api-v1-root'),
	# list of all RNAcentral entries
	url(r'^rna/?$', cache_page(CACHE_TIMEOUT)(views.RnaSequences.as_view()), name='rna-sequences'),
	# single RNAcentral sequence
	url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/?$', cache_page(CACHE_TIMEOUT)(views.RnaDetail.as_view()), name='rna-detail'),
    # view for all cross-references associated with an RNAcentral id
	url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/?$', cache_page(CACHE_TIMEOUT)(views.XrefList.as_view()), name='rna-xrefs'),
    # all literature citations associated with an RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/publications/?$', cache_page(CACHE_TIMEOUT)(views.RnaCitationsView.as_view()), name='rna-publications'),
    # species-specific RNAcentral id
    url(r'^rna/(?P<pk>URS[0-9A-Fa-f]{10})/(?P<taxid>\d+)/?$', cache_page(CACHE_TIMEOUT)(views.RnaSpeciesSpecificView.as_view()), name='rna-species-specific'),
    # literature citations associated with ENA records
    url(r'^accession/(?P<pk>.*?)/citations/?$', cache_page(CACHE_TIMEOUT)(views.CitationView.as_view()), name='accession-citations'),
    # view for an individual cross-reference
    url(r'^accession/(?P<pk>.*?)/info/?$', cache_page(CACHE_TIMEOUT)(views.AccessionView.as_view()), name='accession-detail'),
    # Ensembl-like genome coordinates endpoint
    url(r'^(feature|overlap)/region/(?P<species>\w+)/(?P<chromosome>\w+(\.\d+)?)\:(?P<start>(\d|,)+)-(?P<end>(\d|,)+)/?$',
        cache_page(CACHE_TIMEOUT)(views.GenomeAnnotations.as_view()), name='human-genome-coordinates'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'yaml', 'fasta', 'api', 'gff', 'gff3', 'bed'])

# DAS
urlpatterns += patterns('',
    # DAS-like endpoints
    url(r'^das(?:/sources)?/?$', cache_page(CACHE_TIMEOUT)(views.DasSources.as_view()), name='das-sources'),
    url(r'^das/RNAcentral_GRCh38/features/?$', cache_page(CACHE_TIMEOUT)(views.DasFeatures.as_view()), name='das-features'),
    url(r'^das/RNAcentral_GRCh38/stylesheet/?$', cache_page(CACHE_TIMEOUT)(views.DasStylesheet.as_view()), name='das-stylesheet'),
)

# search
urlpatterns += patterns('',
    url(r'^sequence-search/submit$', 'apiv1.search.sequence.views.submit', name='api-sequence-submit'),
    url(r'^sequence-search/status$', 'apiv1.search.sequence.views.get_status', name='api-sequence-status'),
    url(r'^sequence-search/results$', 'apiv1.search.sequence.views.get_results', name='api-sequence-results'),
)
