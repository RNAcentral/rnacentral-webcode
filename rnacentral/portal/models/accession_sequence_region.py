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


class AccessionSequenceRegion(models.Model):
    id = models.AutoField(primary_key=True)
    region_id = models.ForeignKey(
        "SequenceRegion",
        related_name="accessions",
        db_column="region_id",
        to_field="id",
        on_delete=models.CASCADE,
    )
    accession = models.ForeignKey(
        "Accession",
        related_name="regions",
        db_column="accession",
        to_field="accession",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "rnc_accession_sequence_region"
