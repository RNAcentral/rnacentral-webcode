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
from django.db import connection


class Command(BaseCommand):
    """
    Usage:
    python manage.py update_coordinate_names
    """
    def handle(self, *args, **options):
        """
        Main function, called by django.
        """
        sql = """
        UPDATE rnc_coordinates a
        SET
          name = b.ensembl_name,
          primary_start = local_start,
          primary_end = local_end
        FROM ensembl_insdc_mapping b
        WHERE
          a.primary_accession = b.insdc
          AND a.name IS NULL
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
