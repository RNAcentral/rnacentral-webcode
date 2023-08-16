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


class LitSumm(models.Model):
    id = models.AutoField(primary_key=True)
    rna_id = models.TextField()
    context = models.TextField()
    summary = models.TextField()
    cost = models.FloatField()
    total_tokens = models.IntegerField()
    attempts = models.IntegerField()
    truthful = models.BooleanField()
    problem_summary = models.BooleanField()
    consistency_check_result = models.TextField()
    selection_method = models.TextField()
    rescue_prompts = ArrayField(models.TextField())
    primary_id = models.CharField(max_length=22)

    class Meta:
        db_table = "litsumm_summaries"
        ordering = ["rna_id"]

    def __str__(self):
        return self.rna_id
