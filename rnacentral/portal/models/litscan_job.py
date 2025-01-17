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

from django.db import models


class LitScanJob(models.Model):
    job_id = models.CharField(max_length=100, primary_key=True)
    display_id = models.CharField(max_length=100)
    submitted = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    status = models.CharField(max_length=10)
    hit_count = models.IntegerField()
    query = models.TextField()
    search_limit = models.IntegerField()

    class Meta:
        db_table = "litscan_job"
        ordering = ["job_id"]

    def __str__(self):
        return self.job_id
