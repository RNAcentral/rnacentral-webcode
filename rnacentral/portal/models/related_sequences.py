# -*- coding: utf-8 -*-

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


class RelatedSequence(models.Model):
    id = models.AutoField(primary_key=True)

    source_accession = models.CharField(max_length=50)
    source_urs_taxid = models.ForeignKey(
        'RnaPrecomputed',
        db_column='source_urs_taxid',
        to_field='id',
        null=True,
        related_name='related_sequences',
    )

    target_accession = models.CharField(max_length=50)
    target_urs_taxid = models.ForeignKey(
        'RnaPrecomputed',
        db_column='target_urs_taxid',
        to_field='id',
        null=True,
    )
    relationship_type = models.TextField()
    methods = ArrayField(models.TextField(), null=True)

    class Meta:
        db_table = 'rnc_related_sequences'
