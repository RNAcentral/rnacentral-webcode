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

from django.contrib.sitemaps.views import index

class Command(BaseCommand):
    """
    Usage:
    python manage.py cache_sitemaps
    """

    help = "Generate sitemaps and save them to media directory"

    def add_arguments(self, parser):
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
        self.cache = caches[kwargs['cache_alias']]
        self.timeout = kwargs['timeout']
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX

        # self.cache_index()
        self.cache_sections()

    def cache_index(self):
        print "-" * 80
        print
        print "    Processing index page"
        print
        print "-" * 80

        request = HttpRequest()
        request.META['SERVER_NAME'] = '1.0.0.127.in-addr.arpa'  # important black magic
        request.META['SERVER_PORT'] = '8000'  # important black magic

        view = resolve(reverse('sitemap-index')).func
        response = view(request, sitemaps)  # view is django.contrib.sitemaps.views.index(request, sitemaps) with cache
        response.render()

        request._cache_update_cache = True  # required for CacheMiddleware to cache this response
        cache_key = learn_cache_key(request, response, self.timeout, self.key_prefix, cache=self.cache)
        self.cache.set(cache_key, response, self.timeout)

        # with open(os.path.join(settings.SITEMAPS_ROOT, 'sitemap.xml'), 'w') as index_file:
        #     index_file.write(response.content)

    def cache_sections(self):
        for section, site in sitemaps.items():

            print "-" * 80
            print
            print "    Processing section %s" % section
            print
            print "-" * 80

            if callable(site):
                site = site()

            for page in range(1, site.paginator.num_pages + 1):
                print "Processing page %s of section %s" % (page, section)

                # prepare http request
                request = HttpRequest()
                request.META['SERVER_NAME'] = '1.0.0.127.in-addr.arpa'  # important black magic
                request.META['SERVER_PORT'] = '8000'  # important black magic
                if page > 1:
                    request.GET['p'] = page  # paginate response, if required

                # get response from sitemaps view and render it
                view = resolve(reverse('sitemap-section', kwargs={"section": section})).func
                response = view(request, sitemaps, section=section)  # views.sitemap(request, sitemaps, section="rna")
                response.render()

                # cache response in file system
                request._cache_update_cache = True  # required for CacheMiddleware to cache this response
                cache_key = learn_cache_key(request, response, self.timeout, self.key_prefix, cache=self.cache)
                import pdb
                pdb.set_trace()
                self.cache.set(cache_key, response, self.timeout)

                # request._cache_update_cache = True  # required for CacheMiddleware to cache this response
                # CacheMiddleware(cache_alias='sitemaps', cache_timeout=60*60*355*9).process_response(request, response)

                # with open(os.path.join(settings.SITEMAPS_ROOT, reverse("sitemap-section")), 'w') as index_file:
                #     index_file.write(response.content)
