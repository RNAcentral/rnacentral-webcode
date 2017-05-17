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

from django.conf import settings
from django.conf.urls import patterns, url

from portal import views
from portal.models import get_ensembl_divisions, RnaPrecomputed, Database

urlpatterns = patterns('',
    # homepage
    url(r'^$', 'portal.views.homepage', name='homepage'),
    # unique RNA sequence
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})/?$', 'portal.views.rna_view', name='unique-rna-sequence'),
    # species specific identifier with forward slash
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})/(?P<taxid>\d+)/?$', 'portal.views.rna_view', name='unique-rna-sequence'),
    # species specific identifier with underscore
    url(r'^(?i)rna/(?P<upi>URS[0-9A-F]{10})_(?P<taxid>\d+)/?$', 'portal.views.rna_view_redirect', name='unique-rna-sequence-redirect'),
    # expert database
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)/?$', 'portal.views.expert_database_view', name='expert-database'),
    # expert databases
    url(r'^expert-databases/?$', 'portal.views.expert_databases_view', name='expert-databases'),
    # metadata search can route to any page because it will be taken over by Angular
    url(r'^search/?$', views.TemplateView.as_view(template_name='portal/base.html'), name='metadata-search'),
    # coming soon
    url(r'^(?P<page>coming-soon)/?$', views.StaticView.as_view(), name='coming-soon'),
    # downloads
    url(r'^downloads/?$', views.StaticView.as_view(), {'page': 'downloads'}, name='downloads'),
    # help centre
    url(r'^help/?$', views.StaticView.as_view(), {'page': 'help/faq'}, name='help'),
    url(r'^help/browser-compatibility/?$', views.StaticView.as_view(), {'page': 'help/browser-compatibility'}, name='help-browser-compatibility'),
    url(r'^help/metadata-search/?$', views.StaticView.as_view(), {'page': 'help/metadata-search'}, name='help-metadata-search'),
    url(r'^help/genomic-mapping/?$', views.StaticView.as_view(), {'page': 'help/genomic-mapping', 'divisions': get_ensembl_divisions()}, name='help-genomic-mapping'),
    # training
    url(r'^training/?$', views.StaticView.as_view(), {'page': 'training'}, name='training'),
    # about us
    url(r'^about-us/?$', views.StaticView.as_view(), {'page': 'about', 'blog_url': settings.RELEASE_ANNOUNCEMENT_URL}, name='about'),
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
    url(r'^status/?$', 'portal.views.website_status_view', name='website-status'),
    # genome browser
    url(r'^genome-browser/?$', views.GenomeBrowserView.as_view(), {}, name='genome-browser'),
    # search proxy
    url(r'^api/internal/ebeye/?$', 'portal.views.ebeye_proxy', name='ebeye-proxy'),
    # expert databases
    url(r'^api/internal/expert-dbs/$', views.ExpertDatabasesAPIView.as_view(), {}, name='expert-dbs-api')
)

# internal API
urlpatterns += patterns('',
    # get xrefs table
    url(r'^rna/(?P<upi>\w+)/xrefs/?$', 'portal.views.get_xrefs_data'),
    url(r'^rna/(?P<upi>\w+)/xrefs/(?P<taxid>\d+)/?$', 'portal.views.get_xrefs_data'),
    # get species tree
    url(r'^rna/(?P<upi>\w+)/lineage/?$', 'portal.views.get_sequence_lineage'),
)

# sitemaps
import re

from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap as sitemap_sitemap
from django.core.urlresolvers import reverse
from django.core.cache import caches


class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'homepage', 'about', 'contact-us', 'downloads', 'training',
            'expert-databases', 'nhmmer-sequence-search', 'api-docs',
            'help', 'help-metadata-search', 'help-genomic-mapping', 'help-genomic-mapping',
        ]

    def location(self, item):
        return reverse(item)


class RnaSitemap(Sitemap):
    def items(self):
        return RnaPrecomputed.objects.all()

    def location(self, item):
        if item.taxid is not None:
            return reverse('unique-rna-sequence', kwargs={'upi': item.upi_id, 'taxid': item.taxid})
        else:
            return reverse('unique-rna-sequence', kwargs={'upi': item.upi_id})


class ExpertDatabasesSitemap(Sitemap):
    def items(self):
        return Database.objects.filter(alive='Y').all()

    def location(self, item):
        return reverse('expert-database', kwargs={'expert_db_name': item.descr})

sitemaps = {
    'expert-databases': ExpertDatabasesSitemap,  # GenericSitemap({'queryset': Database.objects.all()}),
    'static': StaticViewSitemap(),
    'rna': RnaSitemap(),
}


def sitemaps_cache(view, cache_alias='sitemaps'):
    def wrapped_view(request, *args, **kwargs):
        cache = caches[cache_alias]
        cache_key = re.sub('[:/#?&=+%]', '_', request.get_full_path())
        response = cache.get(cache_key)
        if response is not None:
            return response
        return view(request, *args, **kwargs)

    return wrapped_view


urlpatterns += patterns('',
    url(r'^sitemap\.xml$', sitemaps_cache(sitemap_index), kwargs={'sitemaps': sitemaps, 'sitemap_url_name': 'sitemap-section'}, name='sitemap-index'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemaps_cache(sitemap_sitemap), kwargs={'sitemaps': sitemaps}, name='sitemap-section')
)
