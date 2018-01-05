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

from __future__ import absolute_import

from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import *

# exporting metadata search results
urlpatterns = [
    # export search results
    url(r'^submit-query/?$',
        submit_export_job,
        name='export-submit-job'),

    # download search results
    url(r'^download-result/?$',
        download_search_result_file,
        name='export-download-result'),

    # get metadata search export status
    url(r'^job-status/?$',
        get_export_job_status,
        name='export-job-status'),

    # interstitial page for a job id
    url(r'^results/?$',
        TemplateView.as_view(template_name='portal/search/export-job-results.html'),
        name='export-job-results'),
]
