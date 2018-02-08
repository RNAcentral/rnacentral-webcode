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

from __future__ import print_function

import warnings

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import index as sitemap_index, sitemap as sitemap_section
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse, resolve
from django.http import HttpRequest

from portal.models import RnaPrecomputed, Database


class Command(BaseCommand):
    """
    Usage:
    python manage.py create_sitemaps
    python manage.py create_sitemaps --section rna --first_page 1 --last_page 21
    python manage.py create_sitemaps --section rna --first_page 20  --last_page 41
    python manage.py create_sitemaps --section rna --first_page 41
    """

    help = "Generate sitemaps and save them to sitemaps directory"

    def add_arguments(self, parser):
        parser.add_argument(
            '--section',
            type=str,
            help='sitemaps consist of sections (e.g. `rna` or `static`); this option allows to process a single section'
        )

        parser.add_argument(
            '--first_page',
            type=int,
            default=1,
            help='create a range of section pages, starting from this one (numeration of pages starts with 1); requires section option'
        )

        parser.add_argument(
            '--last_page',
            type=int,
            default=-1,
            help='create a range of section pages, ending with this (e.g. if --last_page 2, pages = [1, 2]); requires section option'
        )

    def sitemaps(self):
        if self._sitemaps:
            return self._sitemaps
        else:
            class StaticViewSitemap(Sitemap):
                def items(self):
                    return [
                        'homepage', 'about', 'contact-us', 'downloads', 'training',
                        'expert-databases', 'nhmmer-sequence-search', 'api-docs',
                        'help', 'help-text-search', 'help-genomic-mapping', 'help-genomic-mapping',
                    ]

                def location(self, item):
                    return reverse(item)

            class ExpertDatabasesSitemap(Sitemap):
                def items(self):
                    return Database.objects.filter(alive='Y').all()

                def location(self, item):
                    return reverse('expert-database', kwargs={'expert_db_name': item.descr})

            class RnaSitemap(Sitemap):
                def __init__(self, page):
                    self.page = page

                def items(self):
                    paginator = Paginator(RnaPrecomputed.objects.filter(taxid__isnull=False).all(), Sitemap.limit)
                    return paginator.get_page(self.page)

                def location(self, item):
                    return reverse('unique-rna-sequence', kwargs={'upi': item.upi_id, 'taxid': item.taxid})

            self._sitemaps = {
                'expert-databases': ExpertDatabasesSitemap,
                'static': StaticViewSitemap(),
            }

            rna_paginator = Paginator(RnaPrecomputed.objects.filter(taxid__isull=False).all(), Sitemap.limit)
            for page in rna_paginator.page_range:
                key = 'rna-%s' % page
                self._sitemaps[key] = RnaSitemap(page)

            return self._sitemaps

    def handle(self, *args, **kwargs):
        if ('first_page' in kwargs or 'last_page' in kwargs) and 'section' not in kwargs:
            warnings.warn("You must specify '--section' option, to use '--first_page/last_page")
            return

        if kwargs['section'] is not None:
            site = self.sitemaps()[kwargs['section']]
            if callable(site):
                site = site()

            # determine range of pages to be cached
            if kwargs['last_page'] == -1:  # last page is not specified
                last_page = site.paginator.num_pages + 1
            else:  # last page is specified
                last_page = kwargs['last_page'] + 1

            pages = range(kwargs['first_page'], last_page)

            self.create_section(kwargs['section'], pages)
        else:
            self.create_index()
            self.create_sections()

    def create_index(self):
        print("-" * 80)
        print()
        print("    Processing index page")
        print()
        print("-" * 80)

        path = reverse('sitemap', kwargs={"section": "-" + section})
        self.create_path(sitemap_index, path)

    def create_sections(self):
        for section, site in self.sitemaps().items():
            if callable(site):
                site = site()

            pages = range(1, site.paginator.num_pages + 1)
            self.create_section(section, pages)

    def create_section(self, section, pages):
        print("-" * 80)
        print()
        print("    Processing section %s" % section)
        print()
        print("-" * 80)

        for page in pages:
            self.create_section_page(section, page)

    def create_section_page(self, section, page):
        path = reverse('sitemap', kwargs={"section": "-" + section})
        self.create_path(path, path, section, page)

    def create_path(self, path, section=None, page=1):
        # prepare http request
        request = HttpRequest()

        # server name and port don't really matter,
        # cause domain name for sitemaps is taken from django.contrib.sites,
        # but they should exist
        request.META['SERVER_NAME'] = "rnacentral.org"
        request.META['SERVER_PORT'] = "80"
        request.META['REQUEST_METHOD'] = 'GET'
        request.method = 'GET'
        request.path = path

        if page > 1:  # if this is first page, or no pagination is required, don't set GET['p']
            request.META['QUERY_STRING'] = 'p=' + str(page)
            request.GET['p'] = page  # paginate response, if required

        print("Processing %s" % request.get_full_path())

        # get response from sitemaps view and render it
        if section:
            response = sitemap_section(request, self.sitemaps(), section=section)
        else:
            response = sitemap_index(request, **{'sitemaps': self.sitemaps(), 'sitemap_url_name': 'sitemap-section'})
        response.render()
