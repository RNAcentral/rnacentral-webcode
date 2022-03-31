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


class Publication(models.Model):
    """
    To be used by the LitScan Dashboard
    """
    database = models.CharField(max_length=40)
    total_ids = models.IntegerField()
    results = models.IntegerField()

    class Meta:
        db_table = 'publications'
