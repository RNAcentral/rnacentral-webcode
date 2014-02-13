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
from rest_framework.routers import Route, DefaultRouter
from apiv1 import views

class ReadOnlyRouter(DefaultRouter):
    """
    A custom router for read-only urls.
    Required for making trailing slashes optional in all API urls.

    The `suffix` argument is added to the browsable API bread crumbs.
    """
    routes = [
    	# route the list views, e.g. rna-list
        Route(url=r'^{prefix}/?$',
              mapping={'get': 'list'},
              name='{basename}-list',
              initkwargs={'suffix': 'Sequences'}),
        # route the instance views, e.g. rna-detail, accession-detail
        Route(url=r'^{prefix}/{lookup}/?$',
              mapping={'get': 'retrieve'},
              name='{basename}-detail',
              initkwargs={'suffix': 'Sequence'})
    ]

router = ReadOnlyRouter()
# register the urls for the entire RNA viewset.
router.register(r'rna', views.RnaViewSet)

urlpatterns = patterns('',
	# api/current endpoints
    url(r'^current/', include(router.urls)),
    url(r'^current/', include('rest_framework.urls', namespace='current_api', app_name='current_api')),
    # api/v1 endpoints
    url(r'^v1/', include(router.urls)),
    url(r'^v1/', include('rest_framework.urls', namespace='api_v1', app_name='api_v1')),
    # literature citations associated with ENA records
    url(r'^v1/accession/(?P<pk>.*?)/citations/?$', views.CitationView.as_view(), name='accession-citations'),
    # view for individual cross-references
    url(r'^v1/accession/(?P<pk>.*?)/?$', views.AccessionView.as_view(), name='accession-detail'),
    # view for all cross-references associated with an RNAcentral id
	url(r'^v1/rna/(?P<pk>URS[0-9A-Fa-f]{10})/xrefs/?$', views.RnaViewSet.as_view({'get': 'xrefs'}), name='rna-xrefs'),
	# render RNA sequence in fasta format
	url(r'^v1/rna/(?P<pk>URS[0-9A-Fa-f]{10})/fasta/?$', views.RnaFastaView.as_view(), name='rna-fasta'),
)
