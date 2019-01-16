"""
Copyright [2009-2018] EMBL-European Bioinformatics Institute
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

from django.db import models

from django.contrib.postgres.fields import ArrayField

from portal.models import SequenceRegion


class SequenceExon(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(
        SequenceRegion,
        related_name='exons',
        db_column='region_id',
        to_field='id',
        on_delete=models.CASCADE
    )
    exon_start = models.IntegerField()
    exon_stop = models.IntegerField()

    class Meta:
        db_table = 'rnc_sequence_exons'
