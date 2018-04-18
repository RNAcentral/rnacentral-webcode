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

import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Usage:
    python manage.py update_karyotypes
    """
    def fetch_ensembl_karyotype(self, ensembl_url):
        response = requests.get(
            'http://rest.ensembl.org/info/assembly/%s?bands=1' % ensembl_url,
            headers={'Content-Type': 'application/json'}
        )
        if 200 <= response.status_code < 400:
            result = {}
            for data in response.json()["top_level_region"]:
                if data["coord_system"] == "chromosome":
                    start = data["bands"].start if data["bands"].start else 1
                    end = data["bands"].end if data["bands"].end else data["length"]
                    bands = {
                        "id": data["bands"],
                        "start": start,
                        "end": end,
                        "type": data["stain"]
                    }

                    result[data.name] = {
                        "size": data.length,  # or len(data)???
                        "bands": bands
                    }

                return result


    def fetch_ensembl_genomes_karyotypes(self):
        pass


    def handle(self, *args, **options):
        """Main function, called by django."""
        print(self.fetch_ensembl_karyotype('homo_sapiens'))
