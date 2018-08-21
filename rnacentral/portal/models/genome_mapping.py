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

from portal.models.ensembl_assembly import EnsemblAssembly


class GenomeMapping(models.Model):  # (CachingMixin, models.Model):
    assembly_id = models.ForeignKey(EnsemblAssembly, related_name='genome_mappings', db_column='assembly_id')
    chromosome = models.CharField(max_length=100)
    region_id = models.CharField(max_length=100)
    rna_id = models.CharField(max_length=50)
    start = models.IntegerField()
    stop = models.IntegerField()
    identity = models.FloatField()
    strand = models.IntegerField()
    taxid = models.IntegerField()
    upi = models.ForeignKey("Rna", db_column='upi', to_field='upi', related_name='genome_mappings')

    # NOTE: I disabled caching for this model, cause otherwise we run into endless recursion with cache
    # population/invalidation on GenomeBrowser page

    # objects = CachingManager()

    class Meta:
        db_table = 'rnc_genome_mapping'
