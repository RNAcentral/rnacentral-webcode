"""
Copyright [2009-2021] EMBL-European Bioinformatics Institute
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


class QcStatus(models.Model):
    id = models.ForeignKey(
        "RnaPrecomputed",
        primary_key=True,
        db_column="rna_id",
        to_field="id",
        related_name="qc_status",
        on_delete=models.CASCADE,
    )
    upi = models.ForeignKey(
        "Rna",
        db_column="upi",
        to_field="upi",
        related_name="qc_statuses",
        on_delete=models.CASCADE,
    )
    taxid = models.IntegerField()
    has_issue = models.BooleanField()
    incomplete_sequence = models.BooleanField()
    possible_contamination = models.BooleanField()
    missing_rfam_match = models.BooleanField()
    from_repetitive_region = models.BooleanField()
    possible_orf = models.BooleanField()
    messages = models.JSONField()

    class Meta:
        db_table = "qa_status"
        ordering = ["id"]

    def __str__(self):
        return self.id
