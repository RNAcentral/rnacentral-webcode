"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

from caching.base import CachingManager, CachingMixin # django-cache-machine
from django.db import models


class Query(CachingMixin, models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    query = models.TextField()
    length = models.PositiveIntegerField()
    description = models.CharField(max_length=100, null=True)
    # submitted = 
    # finished = 

    objects = CachingManager()

    class Meta:
        db_table = 'nhmmer_query'


class Results(CachingMixin, models.Model):
    id = models.AutoField(primary_key=True)
    query_id = models.ForeignKey('Query', db_column='query_id', related_name='results', db_index=True)
    result_id = models.PositiveIntegerField(db_index=True)
    rnacentral_id = models.CharField(max_length=13, null=True)
    description = models.TextField(null=True)
    bias = models.FloatField(null=True)
    target_length = models.PositiveIntegerField(null=True)
    query_length = models.PositiveIntegerField(null=True)
    alignment = models.TextField(null=True)
    score = models.FloatField(null=True)
    e_value = models.FloatField(null=True)
    alignment_length = models.PositiveIntegerField(null=True)
    match_count = models.PositiveIntegerField(null=True)
    gap_count = models.PositiveIntegerField(null=True)
    nts_count1 = models.PositiveIntegerField(null=True)
    nts_count2 = models.PositiveIntegerField(null=True)
    identity = models.FloatField(null=True)
    query_coverage = models.FloatField(null=True)
    target_coverage = models.FloatField(null=True)
    gaps = models.FloatField(null=True)

    objects = CachingManager()

    class Meta:
        db_table = 'nhmmer_results'
