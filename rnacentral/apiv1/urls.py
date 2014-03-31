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
	url(r'^v1/?$', cache_page(CACHE_TIMEOUT)(views.APIRoot.as_view()), name='api-v1-root'),
	# api/current endpoints
    # url(r'^current/', include('rest_framework.urls', namespace='current_api', app_name='current_api')),
	# list of all RNAcentral entries
	url(r'^v1/rna/?$', cache_page(CACHE_TIMEOUT)(views.RnaList.as_view()), name='rna-list'),
	# single RNAcentral sequence
	url(r'^v1/rna/(?P<pk>URS[0-9A-Fa-f]{10})/?$', cache_page(CACHE_TIMEOUT)(views.RnaDetail.as_view()), name='rna-detail'),
    # view for all cross-references associated with an RNAcentral id
	url(r'^v1/rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/?$', cache_page(CACHE_TIMEOUT)(views.XrefList.as_view()), name='rna-xrefs'),
    # literature citations associated with ENA records
    url(r'^v1/accession/(?P<pk>.*?)/citations/?$', cache_page(CACHE_TIMEOUT)(views.CitationView.as_view()), name='accession-citations'),
    # view for individual cross-references
    # all ENA accessions end with RNA feature name + ordinal
    url(r'^v1/accession/(?P<pk>.*?(RNA|feature)(:\d+)?)/?$', cache_page(CACHE_TIMEOUT)(views.AccessionView.as_view()), name='accession-detail'),
    # Ensembl-like genome coordinates endpoint
    url(r'^v1/feature/region/human/(?P<chromosome>(\d+|Y|X))\:(?P<start>(\d|,)+)-(?P<end>(\d|,)+)/?$',
        cache_page(CACHE_TIMEOUT)(views.GenomeAnnotations.as_view()), name='human-genome-coordinates'),
    # DAS-like endpoints
    url(r'^v1/das(?:/sources)?/?$', cache_page(CACHE_TIMEOUT)(views.DasSources.as_view()), name='das-sources'),
    url(r'^v1/das/RNAcentral_GRCh37/features/?$', cache_page(CACHE_TIMEOUT)(views.DasFeatures.as_view()), name='das-features'),
	url(r'^v1/das/RNAcentral_GRCh37/stylesheet/?$', cache_page(CACHE_TIMEOUT)(views.DasStylesheet.as_view()), name='das-stylesheet'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'yaml', 'fasta', 'api', 'gff', 'gff3', 'bed'])
