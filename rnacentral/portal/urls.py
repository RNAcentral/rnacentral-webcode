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
from django.contrib import admin
from portal import views
from portal.models import get_ensembl_divisions

urlpatterns = patterns('',
    # homepage
    url(r'^$', 'portal.views.homepage', name='homepage'),
    # unique RNA sequence
    url(r'^rna/(?P<upi>URS[0-9A-Fa-f]{10})/?$', 'portal.views.rna_view', name='unique-rna-sequence'),
    # species specific identifier with forward slash
    url(r'^rna/(?P<upi>URS[0-9A-Fa-f]{10})/(?P<taxid>\d+)/?$', 'portal.views.rna_view', name='unique-rna-sequence'),
    # species specific identifier with underscore
    url(r'^rna/(?P<upi>URS[0-9A-Fa-f]{10})_(?P<taxid>\d+)/?$', 'portal.views.rna_view_redirect', name='unique-rna-sequence-redirect'),
    # expert database
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)/?$', 'portal.views.expert_database_view', name='expert-database'),
    # expert databases
    url(r'^expert-databases/?$', 'portal.views.expert_databases_view', name='expert-databases'),
    # metadata search can route to any page because it will be taken over by Angular
    url(r'^search/?$', views.TemplateView.as_view(template_name='portal/base.html')),
    # sequence search
    url(r'^sequence-search/?$', views.StaticView.as_view(), {'page': 'search/sequence-search'}, name='sequence-search'),
    # coming soon
    url(r'^(?P<page>coming-soon)/?$', views.StaticView.as_view(), name='coming-soon'),
    # downloads
    url(r'^downloads/?$', views.StaticView.as_view(), {'page': 'downloads'}, name='downloads'),
    # help centre
    url(r'^help/?$', views.StaticView.as_view(), {'page': 'help/faq'}, name='help'),
    url(r'^help/browser-compatibility/?$', views.StaticView.as_view(), {'page': 'help/browser-compatibility'}, name='help-browser-compatibility'),
    url(r'^help/sequence-search/?$', views.StaticView.as_view(), {'page': 'help/sequence-search'}, name='help-sequence-search'),
    url(r'^help/metadata-search/?$', views.StaticView.as_view(), {'page': 'help/metadata-search'}, name='help-metadata-search'),
    url(r'^help/genomic-mapping/?$', views.StaticView.as_view(), {'page': 'help/genomic-mapping', 'divisions': get_ensembl_divisions()}, name='help-genomic-mapping'),
    # about us
    url(r'^about-us/?$', views.StaticView.as_view(), {'page': 'about'}, name='about'),
    # API documentation
    url(r'^api/?$', views.StaticView.as_view(), {'page': 'help/api-v1'}, name='api-docs'),
    url(r'^api/v2/?$', views.StaticView.as_view(), {'page': 'coming-soon'}, name='api-v2'),
    # contact us
    url(r'^contact/?$', views.ContactView.as_view(), name='contact-us'),
    # contact us success
    url(r'^thanks/?$', views.StaticView.as_view(), {'page': 'thanks'}, name='contact-us-success'),
    # error
    url(r'^error/?$', views.StaticView.as_view(), {'page': 'error'}, name='error'),
    # status
    url(r'^status/?$', 'portal.views.website_status_view', name='website-status'),
)

# internal API
urlpatterns += patterns('',
    # get xrefs table
    url(r'^rna/(?P<upi>\w+)/xrefs/?$', 'portal.views.get_xrefs_data'),
    url(r'^rna/(?P<upi>\w+)/xrefs/(?P<taxid>\d+)/?$', 'portal.views.get_xrefs_data'),
    # get species tree
    url(r'^rna/(?P<upi>\w+)/lineage/?$', 'portal.views.get_sequence_lineage'),
    # query EBeye
    url(r'^api/internal/ebeye/?$', 'portal.views.ebeye_proxy', name='ebeye-proxy'),
    # export search results
    url(r'^api/internal/export-search-results/?$', 'portal.views.export_search_results', name='export-search-results'),
)
