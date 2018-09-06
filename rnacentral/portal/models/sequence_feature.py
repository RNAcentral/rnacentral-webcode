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
from django.contrib.postgres.fields import JSONField


class SequenceFeature(models.Model):
    id = models.AutoField(primary_key=True, db_column='rnc_sequence_features_id')
    accession = models.OneToOneField(
        'Accession',
        db_column='accession',
        to_field='accession',
        related_name='sequence_features',
        null=True
    )
    feature_name = models.CharField(max_length=50)
    metadata = JSONField()
    start = models.IntegerField()
    stop = models.IntegerField()
    taxid = models.IntegerField()
    upi = models.ForeignKey(
        'RNA',
        db_column='upi',
        to_field='upi',
        related_name='sequence_features'
    )

    class Meta:
        db_table = 'rnc_sequence_features'
