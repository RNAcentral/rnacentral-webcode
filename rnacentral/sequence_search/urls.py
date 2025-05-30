"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
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
from django.urls import re_path, reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from .views import *

# sequence search urls
urlpatterns = [
    # launch search
    re_path(r"^submit-job/?$", submit_job, name="sequence-search-submit-job"),
    # get job status
    re_path(
        r"^job-status/(?P<job_id>[A-Za-z0-9_-]+)/?$",
        job_status,
        name="sequence-search-job-status",
    ),
    # get job results
    re_path(
        r"^job-results/(?P<job_id>[A-Za-z0-9_-]+)/?$",
        job_results,
        name="sequence-search-job-results",
    ),
    # get infernal status
    re_path(
        r"^infernal-job-status/(?P<job_id>[A-Za-z0-9_-]+)/?$",
        infernal_job_status,
        name="sequence-search-infernal-job-status",
    ),
    # get infernal results
    re_path(
        r"^infernal-results/(?P<job_id>[A-Za-z0-9_-]+)/?$",
        infernal_job_results,
        name="sequence-search-infernal-job-results",
    ),
    # show searches
    re_path(r"^show-searches/?$", show_searches, name="sequence-search-show-searches"),
    # dashboard
    re_path(r"^dashboard/?$", dashboard, name="sequence-search-dashboard"),
    # help page
    re_path(
        r"^help/?$",
        RedirectView.as_view(url=reverse_lazy("help-sequence-search"), permanent=False),
    ),
    # API documentation
    re_path(
        r"^api/?$",
        TemplateView.as_view(template_name="api.html"),
        name="sequence-search-api",
    ),
    # user interface - embeddable react component
    re_path(
        r"^$",
        TemplateView.as_view(template_name="sequence-search-embed.html"),
        name="sequence-search",
    ),
]
