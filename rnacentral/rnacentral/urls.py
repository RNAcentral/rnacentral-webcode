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

from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework import routers
from portal import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'rna', views.RnaViewSet)

urlpatterns = patterns('',
    url(r'^$', 'portal.views.homepage', name='homepage'),
    url(r'^rna/(?P<upi>\w+)/?$', 'portal.views.rna_view'),
    # admin
    url(r'^admin/?', include(admin.site.urls)),
    # flat pages
    url(r'^(?P<page>about|help|thanks|coming-soon)/?$', views.StaticView.as_view()),
    url(r'^docs/(?P<page>genome-browsers)/?$', views.StaticView.as_view()),
    url(r'^(?P<page>expert-databases)/?$', views.StaticView.as_view(), name='expert_databases'),
    # contact us
    url(r'^contact/?$', views.ContactView.as_view()),
    # django-rest-framework API, use trailing slashes
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/v1/', include('rest_framework.urls', namespace='rest_framework')),
    # temporary API
    url(r'^xref/(?P<accession>.+)/refs/?$', 'portal.views.get_literature_references'),
    url(r'^expert-database/(?P<expert_db_name>.+)/lineage/?$', 'portal.views.get_expert_database_organism_sunburst'),
    url(r'^rna/(?P<upi>\w+)/xrefs/?$', 'portal.views.get_xrefs_data'),
    url(r'^rna/(?P<upi>\w+)/lineage/?$', 'portal.views.get_sequence_lineage'),
    # robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # expert databases
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)/?$', 'portal.views.expert_database_view', name='expert_database'),
    # status page
    url(r'^status/?', 'portal.views.website_status_view'),
)
