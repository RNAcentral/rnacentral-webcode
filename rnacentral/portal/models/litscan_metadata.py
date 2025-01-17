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


class LitScanMetadata(models.Model):
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    primary_id = models.CharField(max_length=255)

    class Meta:
        db_table = "litscan_database"
        ordering = ["id"]

    def __str__(self):
        return self.id
