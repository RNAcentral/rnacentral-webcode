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
from django.core import paginator

from portal.models import RnaPrecomputed


class Command(BaseCommand):
    """
    Usage:
    python manage.py cache_sitemaps
    """

    help = "Check if random access to queryset page is time-constant or linear, or slower"

    def add_arguments(self, parser):
        parser.add_argument(
            'page',
            type=int,
            help='page'
        )


    def handle(self, *args, **kwargs):
        page = kwargs['page']

        rna_paginator = paginator.Paginator(RnaPrecomputed.objects.all(), 50000)
        from django.db import connection
        message = ""
        for object in rna_paginator.page(page).object_list:
            message = message + str(object.upi_id)
            # message = message + str(object.id)
        print connection.queries