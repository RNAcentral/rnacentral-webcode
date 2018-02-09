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

import os
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

    Note that we don't use pagination withing each section - instead, we create
    a separate section instead of pages. E.g. if rna section were to contain
    100,000 objects, we would create 2 sections rna-1 and rna-2.

    We'll be calling rna a section and rna-1 and rna-2 pages (although in django
    sitemaps terms they are separate sections).
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
        if hasattr(self, "_sitemaps"):
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

            # handle rna pages sub-sectioning
            rna_queryset = RnaPrecomputed.objects.filter(taxid__isnull=False).all().order_by('upi')
            rna_paginator = Paginator(rna_queryset, Sitemap.limit)

            class RnaSitemap(Sitemap):
                def __init__(self, page_number, rna_paginator):
                    self.page_number = page_number
                    self.rna_paginator = rna_paginator

                @property
                def paginator(self):
                    output = type('paginator', (), {})()
                    output.num_pages = 1
                    return output

                def items(self):
                    return self.rna_paginator.page(self.page_number)

                def location(self, item):
                    return reverse('unique-rna-sequence', kwargs={'upi': item.upi_id, 'taxid': item.taxid})

            self._sitemaps = {
                'expert-databases': ExpertDatabasesSitemap,
                'static': StaticViewSitemap(),
            }

            for page_number in rna_paginator.page_range:
                key = '-rna-%s' % page_number
                self._sitemaps[key] = RnaSitemap(page_number, rna_paginator)

            return self._sitemaps

    def handle(self, *args, **kwargs):
        if ('first_page' in kwargs or 'last_page' in kwargs) and 'section' not in kwargs:
            warnings.warn("You must specify '--section' option, to use '--first_page/last_page")
            return

        if kwargs['section'] is not None:
            site = self.sitemaps()[kwargs['section']]
            if callable(site):
                site = site()

            if kwargs['section'] == 'rna':
                # determine range of pages to be cached
                if kwargs['last_page'] == -1:  # last page is not specified
                    last_page = site.paginator.num_pages
                else:  # last page is specified
                    last_page = kwargs['last_page']

                # create section's sitemap
                pages = range(kwargs['first_page'], last_page + 1)
                for page_number in pages:
                    self.create_section("-" + kwargs['section'] + "-" + str(page_number))
            else:
                warnings.warn("only rna section is currently supported")
                return

        else:
            self.create_index()

    def create_index(self):
        print("-" * 80)
        print()
        print("    Processing index page")
        print()
        print("-" * 80)

        request = self.prepare_request()
        sitemaps = self.sitemaps()
        response = sitemap_index(request, **{'sitemaps': sitemaps, 'sitemap_url_name': 'sitemap'})
        self.write_response(response, "")  # for index sitemap section is empty string

        for section in self.sitemaps().keys():
            self.create_section(section)

    def create_section(self, section):
        print("-" * 80)
        print()
        print("    Processing section %s" % section)
        print()
        print("-" * 80)

        request = self.prepare_request()
        response = sitemap_section(request, self.sitemaps(), section=section)
        self.write_response(response, section)

    def prepare_request(self):
        """Manually create HttpRequest for django sitemaps views to process"""
        # prepare http request
        request = HttpRequest()

        # server name and port don't really matter,
        # cause domain name for sitemaps is taken from django.contrib.sites,
        # but they should exist
        request.META['SERVER_NAME'] = "rnacentral.org"
        request.META['SERVER_PORT'] = "80"
        request.META['REQUEST_METHOD'] = 'GET'
        request.method = 'GET'

        return request

    def write_response(self, response, section):
        """Writes HttpResponse into a file"""
        filename = os.path.join(settings.PROJECT_PATH, 'rnacentral', 'sitemaps', 'sitemap%s.xml' % section)
        response.render()
        open(filename, 'w').write(response.content)
