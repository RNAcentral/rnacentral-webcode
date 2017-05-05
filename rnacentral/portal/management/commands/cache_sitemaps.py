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

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse, resolve
from django.conf import settings
from django.contrib.sitemaps import views
from django.http import HttpRequest

from portal.urls import sitemaps

class Command(BaseCommand):
    """
    Usage:
    python manage.py cache_sitemaps
    """

    help = "Generate sitemaps and save them to media directory"

    def handle(self, *args, **options):
        self.cache_index()
        self.cache_sections()

    def cache_index(self):
        request = HttpRequest()
        request.META['SERVER_NAME'] = '1.0.0.127.in-addr.arpa'  # important black magic
        request.META['SERVER_PORT'] = '8000'  # important black magic
        response = views.index(request, sitemaps)  # or resolve(reverse("sitemap-index")).func(request, sitemaps)
        response.render()

        with open(os.path.join(settings.SITEMAPS_ROOT, 'sitemap.xml'), 'w') as index_file:
            index_file.write(response.content)

    def cache_sections(self):
        request = HttpRequest()
        request.META['SERVER_NAME'] = '1.0.0.127.in-addr.arpa'  # important black magic
        request.META['SERVER_PORT'] = '8000'  # important black magic
        response = views.sitemap(request, sitemaps, section="rna")
        response.render()

        # with open(os.path.join(settings.SITEMAPS_ROOT, reverse("sitemap-section")), 'w') as index_file:
        #     index_file.write(response.content)
