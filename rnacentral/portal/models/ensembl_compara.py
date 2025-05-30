"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
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

from .rna_precomputed import RnaPrecomputed


class EnsemblCompara(models.Model):
    id = models.IntegerField(primary_key=True)
    ensembl_transcript_id = models.TextField()
    urs_taxid = models.ForeignKey(
        RnaPrecomputed, to_field="id", db_column="urs_taxid", on_delete=models.CASCADE
    )
    homology_id = models.IntegerField()

    class Meta:
        db_table = "ensembl_compara"
        ordering = ["ensembl_transcript_id"]

    def __str__(self):
        return self.id
