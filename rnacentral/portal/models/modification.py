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


class Modification(CachingMixin, models.Model):
    """Describe modified nucleotides at certain sequence positions reported in xrefs."""
    id = models.AutoField(primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', related_name='modifications')
    xref = models.ForeignKey('Xref', db_column='accession', to_field='accession', related_name='modifications')
    position = models.PositiveIntegerField()  # absolute sequence position, always > 0
    author_assigned_position = models.IntegerField()  # can be negative, e.g. 3I2S chain A
    modification_id = models.ForeignKey('ChemicalComponent', db_column='modification_id')

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_modifications'