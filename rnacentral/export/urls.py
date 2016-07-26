"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

# exporting metadata search results
urlpatterns = patterns('',
    # export search results
    url(r'^submit-query/?$',
        'export.views.submit_export_job',
        name='export-submit-job'),

    # download search results
    url(r'^download-result/?$',
        'export.views.download_search_result_file',
        name='export-download-result'),

    # get metadata search export status
    url(r'^job-status/?$',
        'export.views.get_export_job_status',
        name='export-job-status'),

    # interstitial page for a job id
    url(r'^results/?$',
        TemplateView.as_view(template_name='portal/search/export-job-results.html'),
        name='export-job-results'),
)
