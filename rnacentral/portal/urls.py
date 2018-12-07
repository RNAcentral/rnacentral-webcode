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

from django.conf import settings
from django.conf.urls import url
from django.http import FileResponse, Http404

from portal import views
from portal.models import EnsemblAssembly

urlpatterns = [
    # homepage
    url(r'^$', views.homepage, name='homepage'),
    # unique RNA sequence
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})/?$', views.rna_view, name='unique-rna-sequence'),
    # species specific identifier with forward slash
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})/(?P<taxid>\d+)/?$', views.rna_view, name='unique-rna-sequence'),
    # species specific identifier with underscore
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})_(?P<taxid>\d+)/?$', views.rna_view_redirect, name='unique-rna-sequence-redirect'),
    # expert database
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)/?$', views.expert_database_view, name='expert-database'),
    # expert databases
    url(r'^expert-databases/?$', views.expert_databases_view, name='expert-databases'),
    # text search can route to any page because it will be taken over by Angular
    url(r'^search/?$', views.TemplateView.as_view(template_name='portal/base.html'), name='text-search'),
    # coming soon
    url(r'^(?P<page>coming-soon)/?$', views.StaticView.as_view(), name='coming-soon'),
    # downloads
    url(r'^downloads/?$', views.StaticView.as_view(), {'page': 'downloads'}, name='downloads'),
    # external link
    url(r'^link/(?P<expert_db>[-\w]+)\:(?P<external_id>.+?)/?$', views.external_link, name='external-link'),
    # help centre
    url(r'^help/?$', views.StaticView.as_view(), {'page': 'help/faq'}, name='help'),
    url(r'^help/browser-compatibility/?$', views.StaticView.as_view(), {'page': 'help/browser-compatibility'}, name='help-browser-compatibility'),
    url(r'^help/text-search/?$', views.StaticView.as_view(), {'page': 'help/text-search'}, name='help-text-search'),
    url(r'^help/rfam-annotations/?$', views.StaticView.as_view(), {'page': 'help/rfam-annotations'}, name='help-rfam-annotations'),
    url(r'^help/rna-target-interactions/?$', views.StaticView.as_view(), {'page': 'help/rna-target-interactions'}, name='help-rna-target-interactions'),
    url(r'^help/gene-ontology-annotations/?$', views.StaticView.as_view(), {'page': 'help/gene-ontology-annotations'}, name='help-gene-ontology-annotations'),
    url(r'^help/genomic-mapping/?$', views.StaticView.as_view(), {'page': 'help/genomic-mapping', 'assemblies': EnsemblAssembly.objects.all()}, name='help-genomic-mapping'),
    url(r'^help/link-to-rnacentral/?$', views.StaticView.as_view(), {'page': 'help/link-to-rnacentral'}, name='linking-to-rnacentral'),
    url(r'^help/conserved-motifs/?$', views.StaticView.as_view(), {'page': 'help/conserved-motifs'}, name='help-conserved-motifs'),
    url(r'^help/public-database/?$', views.StaticView.as_view(), {'page': 'help/public-database'}, name='help-public-database'),
    # training
    url(r'^training/?$', views.StaticView.as_view(), {'page': 'training'}, name='training'),
    # about us
    url(r'^about-us/?$', views.StaticView.as_view(), {'page': 'about', 'blog_url': settings.RELEASE_ANNOUNCEMENT_URL}, name='about'),
    # use cases
    url(r'^use-cases/?$', views.StaticView.as_view(), {'page': 'use-cases'}, name='use-cases'),
    # API documentation
    url(r'^api/?$', views.StaticView.as_view(), {'page': 'help/api-v1'}, name='api-docs'),
    url(r'^api/v2/?$', views.StaticView.as_view(), {'page': 'coming-soon'}, name='api-v2'),
    # contact us
    url(r'^contact/?$', views.ContactView.as_view(), name='contact-us'),
    # contact us success
    url(r'^thanks/?$', views.StaticView.as_view(), {'page': 'thanks'}, name='contact-us-success'),
    # error
    url(r'^error/?$', views.StaticView.as_view(), {'page': 'error'}, name='error'),
    # status
    url(r'^status/?$', views.website_status_view, name='website-status'),
    # genome browser
    url(r'^genome-browser/?$', views.GenomeBrowserView.as_view(), {}, name='genome-browser'),
    # proxy for ebeye search and rfam images
    url(r'^api/internal/proxy/?$', views.proxy, name='proxy'),
]

# internal API
urlpatterns += [
    # get species tree
    url(r'^rna/(?P<upi>\w+)/lineage/?$', views.get_sequence_lineage, name='sequence-lineage'),
]


# sitemaps
def sitemaps(request, section):
    try:
        # section is either empty string for sitemaps index or
        # string e.g. "-expert-databases", note the dash in the beginning
        path_to_xml_file = os.path.join(settings.PROJECT_PATH, 'rnacentral', 'sitemaps', 'sitemap%s.xml' % section)
        xml_file = open(path_to_xml_file, 'rb')
        return FileResponse(xml_file, content_type='text/xml')
    except IOError as e:
        raise Http404

urlpatterns += [
    url(r'^sitemap(?P<section>.*)\.xml$', sitemaps, name='sitemap')
]
