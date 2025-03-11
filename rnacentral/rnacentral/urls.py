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

import os

from django.urls import include, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # RNAcentral portal
    re_path(r"", include("portal.urls")),
    # REST API (use trailing slashes)
    re_path(r"^api/current/", include("apiv1.urls")),
    re_path(r"^api/v1/", include("apiv1.urls")),
    # export text search results
    re_path(r"^export/", include("export.urls")),
    # new sequence search
    re_path(r"^sequence-search/", include("sequence_search.urls")),
    # Django Debug Toolbar
    # OpenAPI schema
    re_path(r"^api/schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^api/schema/swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# robots.txt extras
# use the RNACENTRAL_ENV variable to set the correct robots.txt file
if "dev" in os.environ.get("RNACENTRAL_ENV", ""):
    additional_settings = [
        re_path(
            r"^robots\.txt$",
            TemplateView.as_view(
                template_name="robots-test.txt", content_type="text/plain"
            ),
        ),
    ]
else:
    additional_settings = [
        re_path(
            r"^robots\.txt$",
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        ),
    ]

urlpatterns += additional_settings


# Override 500 page, so that in case of an error, we still display our error page with normal response status
# and EBI load balancer still proxies to our website instead of showing an EBI 'service down' page
handler500 = "portal.views.handler500"
