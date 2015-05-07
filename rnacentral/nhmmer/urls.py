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

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from settings import MIN_LENGTH, MAX_LENGTH
import views


# nhmmer sequence search urls
urlpatterns = patterns('',
    # launch nhmmer search
    url(r'^submit-query/?$',
        'nhmmer.views.submit_job',
        name='nhmmer-submit-job'),

    # cancel search results
    url(r'^cancel-job/?$',
        'nhmmer.views.cancel_job',
        name='nhmmer-cancel-job'),

    # get nhmmer search job status
    url(r'^job-status/?$',
        'nhmmer.views.get_status',
        name='nhmmer-job-status'),

    # get nhmmer results
    url(r'^get-results/?$',
        views.ResultsView.as_view(),
        name='nhmmer-job-results'),

    # get query details
    url(r'^query-info/?$',
        views.QueryView.as_view(),
        name='nhmmer-query-info'),

    # dashboard
    url(r'^dashboard/?$',
        'nhmmer.views.dashboard_view',
        name='nhmmer-dashboard'),
)


class SequenceSearchUIView(TemplateView):
    """
    Class-based view for displaying sequence search
    user interface.
    """
    template_name='nhmmer/sequence-search.html'

    def get_context_data(self, **kwargs):
        """
        Override the default method in order to pass
        additional data to the template.
        """
        context = super(TemplateView, self).get_context_data(**kwargs)
        context.update({
            'MIN_LENGTH': MIN_LENGTH,
            'MAX_LENGTH': MAX_LENGTH,
        })
        return context


urlpatterns += patterns('',
    # user interface
    url(r'^$', SequenceSearchUIView.as_view(),
        name='nhmmer-sequence-search'),
)
