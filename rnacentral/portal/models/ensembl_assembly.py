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

from caching.base import CachingManager, CachingMixin
from django.db import models


class EnsemblAssembly(CachingMixin, models.Model):
    assembly_id = models.CharField(primary_key=True, max_length=255)
    assembly_full_name = models.CharField(max_length=255, db_index=True)
    gca_accession = models.CharField(max_length=20, db_index=True, null=True)
    assembly_ucsc = models.CharField(max_length=100, db_index=True, null=True)
    common_name = models.CharField(max_length=255, db_index=True, null=True)
    taxid = models.IntegerField(db_index=True, unique=True)
    ensembl_url = models.CharField(max_length=100, db_index=True, null=True)
    division = models.CharField(max_length=20, db_index=True, null=True)
    subdomain = models.CharField(max_length=100, db_index=True, default="ensembl.org")
    example_chromosome = models.CharField(max_length=20, null=True)
    example_start = models.IntegerField(null=True)
    example_end = models.IntegerField(null=True)
    selected_genome = models.BooleanField(default=False)

    objects = CachingManager()

    def get_human_readable_ensembl_url(self):
        return self.ensembl_url.replace("_", " ").capitalize()

    class Meta:
        db_table = "ensembl_assembly"
        ordering = ["assembly_full_name"]

    def __str__(self):
        return self.assembly_full_name
