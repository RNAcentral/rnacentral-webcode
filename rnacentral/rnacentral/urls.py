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

import socket

from django.conf.urls import url, include, handler500
from django.views.generic import TemplateView


urlpatterns = [
    # RNAcentral portal
    url(r'', include('portal.urls')),
    # REST API (use trailing slashes)
    url(r'^api/current/', include('apiv1.urls')),
    url(r'^api/v1/', include('apiv1.urls')),
    # export text search results
    url(r'^export/', include('export.urls')),
    # sequence search
    url(r'^sequence-search/', include('nhmmer.urls')),
]

# robots.txt extras
if 'hx' in socket.gethostname():
    additional_settings = [
      url(r'^robots\.txt$', TemplateView.as_view(template_name='robots-test.txt', content_type='text/plain')),
    ]
else:
    additional_settings = [
      url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    ]

urlpatterns += additional_settings


# Override 500 page, so that in case of an error, we still display our error page with normal response status
# and EBI load balancer still proxies to our website instead of showing an EBI 'service down' page
handler500 = 'portal.views.handler500'

