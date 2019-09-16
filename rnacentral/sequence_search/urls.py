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
from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import *


# sequence search urls
urlpatterns = [
    # launch search
    url(r'^submit-job/?$',
        submit_job,
        name='sequence-search-submit-job'),

    # get job status
    url(r'^job-status/(?P<job_id>[A-Za-z0-9_-]+)/?$',
        job_status,
        name='sequence-search-job-status'),

    # get job results
    url(r'^job-results/(?P<job_id>[A-Za-z0-9_-]+)/?$',
        job_results,
        name='sequence-search-job-results'),

    # show searches
    url(r'^show-searches/?$',
        show_searches,
        name='sequence-search-show-searches'),

    # dashboard
    url(r'^dashboard/?$',
        dashboard,
        name='sequence-search-dashboard'),

    # user interface
    url(r'^$', TemplateView.as_view(template_name='sequence-search.html'), name='nhmmer-sequence-search'),
]
