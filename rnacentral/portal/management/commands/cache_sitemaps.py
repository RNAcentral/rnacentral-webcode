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
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse, resolve
from django.conf import settings
from django.http import HttpRequest
from django.utils.cache import learn_cache_key
from django.core.cache import caches

from portal.urls import sitemaps


class Command(BaseCommand):
    """
    Usage:
    python manage.py cache_sitemaps
    """

    help = "Generate sitemaps and save them to media directory"

    def add_arguments(self, parser):
        parser.add_argument(
            '--server_name',
            type=str,
            default='rnacentral.org',
            help='domain name of the machine, that we generate sitemaps for e.g. rnacentral.org'
        )

        parser.add_argument(
            '--server_port',
            type=str,
            default='80',
            help='port number of the machine, e.g. 80'
        )

        parser.add_argument(
            '--section',
            type=str,
            help='a section of sitemaps (e.g. rna or static), if you want only it to be processed'
        )

        parser.add_argument(
            '--page',
            type=int,
            help='a particular page of section to be cached'
        )

        parser.add_argument(
            '--cache_alias',
            type=str,
            default='sitemaps',
            help='a cache to use - pick one from your settings.CACHES'

        )

        parser.add_argument(
            '--timeout',
            type=int,
            default=60 * 60 * 355 * 9,
            help='how long to keep sitemaps cached'
        )

    def handle(self, *args, **kwargs):
        self.server_name = kwargs['server_name']
        self.server_port = kwargs['server_port']

        self.cache = caches[kwargs['cache_alias']]
        self.timeout = kwargs['timeout']
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX

        if 'section' in kwargs:
            if 'page' in kwargs:
                self.cache_section(kwargs['section'], site, kwargs['page'])
            else:
                self.cache_section(kwargs['section'], site)
        else:
            # self.cache_index()
            self.cache_sections()

    def cache_index(self):
        print "-" * 80
        print
        print "    Processing index page"
        print
        print "-" * 80

        view = resolve(reverse('sitemap-index')).func  # django.contrib.sitemaps.views.index(request, sitemaps) with cache
        self.cache_view(view, sitemaps)

    def cache_sections(self):
        for section, site in sitemaps.items():
            if callable(site):
                site = site()

            self.cache_section(section, site)

    def cache_section(self, section, site, page=None):
        print "-" * 80
        print
        print "    Processing section %s" % section
        print
        print "-" * 80

        if page:
            self.cache_page(self, section, page)
        else:
            for page in range(1, site.paginator.num_pages + 1):
                self.cache_page(self, section, page)

    def cache_page(self, section, page):
        print "Processing page %s of section %s" % (page, section)

        view = resolve(reverse('sitemap-section', kwargs={
            "section": section})).func  # django.contrib.sitemaps.views.sitemap(request, sitemaps, section="rna")
        self.cache_view(view, sitemaps, section, page)

    def cache_view(self, view, sitemaps, section=None, page=1):
        # prepare http request
        request = HttpRequest()
        request.META['SERVER_NAME'] = self.server_name  # important
        request.META['SERVER_PORT'] = self.server_port  # important

        # if this is first page, or no pagination is required, don't set GET['p']
        if page > 1:
            request.GET['p'] = page  # paginate response, if required

        # get response from sitemaps view and render it
        if section:
            response = view(request, sitemaps, section=section)
        else:
            response = view(request, sitemaps)
        response.render()

        # cache rendered response in file system
        cache_key = learn_cache_key(request, response, self.timeout, self.key_prefix, cache=self.cache)
        self.cache.set(cache_key, response, self.timeout)
