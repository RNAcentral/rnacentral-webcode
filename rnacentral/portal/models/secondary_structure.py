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

from django.db import models


class SecondaryStructure(models.Model):
    id = models.AutoField(primary_key=True)
    accession = models.OneToOneField(
        'Accession',
        db_column='rnc_accession_id',
        to_field='accession',
        related_name='secondary_structure',
    )
    secondary_structure = models.TextField()
    md5 = models.CharField(max_length=32, db_index=True)

    class Meta:
        db_table = 'rnc_secondary_structure'
        unique_together = (('accession', 'md5'),)


class SecondarStructureWithLayout(models.Model):
    id = models.AutoField(primary_key=True)
    secondary_structure = models.TextField()
    urs = models.OneToOneField(
        'Rna',
        db_column='urs',
        to_field='upi',
        related_name='secondary_structure_layout',
    )
    model = models.TextField()
    layout = models.TextField()

    class Meta:
        db_table = 'rnc_secondary_structure_layout'
        unique_together = (('urs',),)
