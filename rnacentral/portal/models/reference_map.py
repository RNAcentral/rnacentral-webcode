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
from portal.models.accession import Accession
from portal.models.reference import Reference


class Reference_map(models.Model):
    accession = models.ForeignKey(
        Accession,
        db_column="accession",
        to_field="accession",
        related_name="refs",
        on_delete=models.CASCADE,
    )
    data = models.ForeignKey(
        Reference, db_column="reference_id", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "rnc_reference_map"
        ordering = ["id"]

    def __str__(self):
        return self.id
