"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
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

from django.contrib.postgres.fields import ArrayField
from django.db import models
from portal.models import RnaPrecomputed


class SequenceRegionActive(models.Model):
    id = models.AutoField(primary_key=True)
    urs_taxid = models.ForeignKey(
        RnaPrecomputed,
        related_name="regions_active",
        db_column="urs_taxid",
        to_field="id",
        on_delete=models.CASCADE,
    )
    region_name = models.TextField()
    chromosome = models.TextField()
    strand = models.IntegerField()
    region_start = models.IntegerField()
    region_stop = models.IntegerField()
    assembly_id = models.CharField(max_length=255)
    was_mapped = models.BooleanField()
    identity = models.FloatField()
    exon_count = models.IntegerField()

    class Meta:
        db_table = "rnc_sequence_regions_active"
        ordering = ["urs_taxid"]
