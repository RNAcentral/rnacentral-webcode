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

from caching.base import CachingMixin, CachingManager
from django.db import models

from portal.models import EnsemblAssembly, GenomicCoordinates


class EnsemblInsdcMapping(CachingMixin, models.Model):
    assembly_id = models.ForeignKey(EnsemblAssembly, related_name='assembly', db_column='assembly_id')
    insdc = models.CharField(max_length=255, db_index=True)
    ensembl_name = models.CharField(max_length=255, db_index=True)

    objects = CachingManager()

    class Meta:
        db_table = 'ensembl_insdc_mapping'
