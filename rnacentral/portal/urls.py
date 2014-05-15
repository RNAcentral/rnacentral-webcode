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

urlpatterns = patterns('',
    # homepage
    url(r'^$', 'portal.views.homepage', name='homepage'),
    # unique RNA sequence
    url(r'^rna/(?P<upi>URS[0-9A-Fa-f]{10})/?$', 'portal.views.rna_view', name='unique-rna-sequence'),
    # expert database
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)/?$', 'portal.views.expert_database_view', name='expert-database'),
    # expert databases
    url(r'^expert-databases/?$', views.StaticView.as_view(), {'page': 'expert-databases'}, name='expert-databases'),
    # metadata search can route to any page because it will be taken over by Angular
    url(r'^search/?$', 'portal.views.homepage'),
    # sequence search
    url(r'^sequence-search/?$', views.StaticView.as_view(), {'page': 'sequence-search'}, name='sequence-search'),
    # coming soon
    url(r'^(?P<page>coming-soon)/?$', views.StaticView.as_view(), name='coming-soon'),
    # downloads
    url(r'^downloads/?$', views.StaticView.as_view(), {'page': 'downloads'}, name='downloads'),
    # help centre
    url(r'^help/?$', views.StaticView.as_view(), {'page': 'help'}, name='help'),
    # about us
    url(r'^about-us/?$', views.StaticView.as_view(), {'page': 'about'}, name='about'),
    # API documentation
    url(r'^api/?$', views.StaticView.as_view(), {'page': 'api-v1'}, name='api-docs'),
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
    # get organism sunburst
    url(r'^expert-database/(?P<expert_db_name>.+)/lineage/?$', 'portal.views.get_expert_database_organism_sunburst'),
    # get xrefs table
    url(r'^rna/(?P<upi>\w+)/xrefs/?$', 'portal.views.get_xrefs_data'),
    # get species tree
    url(r'^rna/(?P<upi>\w+)/lineage/?$', 'portal.views.get_sequence_lineage'),
    # query EBeye
    url(r'^api/internal/ebeye/?$', 'portal.views.ebeye_proxy', name='ebeye-proxy'),
)
