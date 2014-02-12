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
    A router for read-only APIs, which accepts optional trailing slashes.
    """
    routes = [
        Route(url=r'^{prefix}/?$',
              mapping={'get': 'list'},
              name='{basename}-list',
              initkwargs={'suffix': 'Sequences'}),
        Route(url=r'^{prefix}/{lookup}/?$',
              mapping={'get': 'retrieve'},
              name='{basename}-detail',
              initkwargs={'suffix': 'Sequence'})
    ]

router = ReadOnlyRouter()
router.register(r'rna', views.RnaViewSet)

urlpatterns = patterns('',
    url(r'^current/', include(router.urls)),
    url(r'^current/', include('rest_framework.urls', namespace='current_api', app_name='current_api')),
    url(r'^v1/', include(router.urls)),
    url(r'^v1/', include('rest_framework.urls', namespace='api_v1', app_name='api_v1')),
    url(r'^v1/accession/(?P<pk>.*?)/citations/?$', views.CitationView.as_view(), name='accession-citations'),
    url(r'^v1/accession/(?P<pk>.*?)/?$', views.AccessionView.as_view(), name='accession-detail'),
	url(r'^v1/rna/(?P<pk>UPI[0-9A-Fa-f]{10})/xrefs/?$', views.RnaViewSet.as_view({'get': 'xrefs'}), name='rna-xrefs'),
)
