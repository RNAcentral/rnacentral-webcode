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


class RnaPrecomputed(models.Model):
    id = models.CharField(max_length=22, primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', to_field='upi', related_name='precomputed')
    taxid = models.IntegerField(db_index=True, null=True)
    description = models.CharField(max_length=250)
    rna_type = models.CharField(max_length=250)
    rfam_problems = models.TextField(default='')

    class Meta:
        db_table = 'rnc_rna_precomputed'
