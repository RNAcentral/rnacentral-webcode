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

from django.core.management.base import BaseCommand
from portal.models import EnsemblAssembly
from portal.models import SequenceRegion


def update_example_locations():
    """
    """
    for assembly in EnsemblAssembly.objects.filter(example_chromosome__isnull=True).all():
        try:
            region = SequenceRegion.objects.filter(assembly_id=assembly.assembly_id).all()[:1].get()
            print(assembly.assembly_id, region.chromosome, region.region_start, region.region_stop)
            assembly.example_chromosome = region.chromosome
            assembly.example_start = region.region_start
            assembly.example_end = region.region_stop
            assembly.save()
        except SequenceRegion.DoesNotExist:
            print(assembly.assembly_id + ' does not exist')


class Command(BaseCommand):
    """
    Usage:
    python manage.py update_ensembl_assembly
    """
    def handle(self, *args, **options):
        """Main function, called by django."""
        update_example_locations()
