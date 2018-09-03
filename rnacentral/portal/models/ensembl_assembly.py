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

from caching.base import CachingMixin, CachingManager
from django.db import models

import portal.models.genome_mapping


class EnsemblAssembly(CachingMixin, models.Model):
    assembly_id = models.CharField(primary_key=True, max_length=255)
    assembly_full_name = models.CharField(max_length=255, db_index=True)
    gca_accession = models.CharField(max_length=20, db_index=True, null=True)
    assembly_ucsc = models.CharField(max_length=100, db_index=True, null=True)
    common_name = models.CharField(max_length=255, db_index=True, null=True)
    taxid = models.IntegerField(db_index=True, unique=True)
    ensembl_url = models.CharField(max_length=100, db_index=True, null=True)
    division = models.CharField(max_length=20, db_index=True, null=True)
    subdomain = models.CharField(max_length=100, db_index=True, default='ensembl.org')
    example_chromosome = models.CharField(max_length=20, null=True)
    example_start = models.IntegerField(null=True)
    example_end = models.IntegerField(null=True)

    objects = CachingManager()

    def get_human_readable_ensembl_url(self):
        return self.ensembl_url.replace("_", " ").capitalize()

    @classmethod
    def get_assemblies_with_example_locations(cls):
        query = '''
            SELECT 1 as id, {ensembl_assembly}.assembly_id, assembly_full_name, gca_accession, assembly_ucsc,
              common_name, taxid, ensembl_url, division, subdomain,
              example_chromosome, example_start, example_end,
              start, stop, chromosome
            FROM {ensembl_assembly}
            JOIN (
              SELECT DISTINCT ON ({genome_mapping}.assembly_id)
                {genome_mapping}.assembly_id, {genome_mapping}.start, {genome_mapping}.stop, {genome_mapping}.chromosome
              FROM {genome_mapping}
            ) mapping
            ON mapping.assembly_id = {ensembl_assembly}.assembly_id
            ORDER BY {ensembl_assembly}.ensembl_url ASC
        '''.format(
            genome_mapping=portal.models.genome_mapping.GenomeMapping._meta.db_table,
            ensembl_assembly=EnsemblAssembly._meta.db_table
        )

        # this won't really paginate
        return list(EnsemblAssembly.objects.raw(query))

    class Meta:
        db_table = 'ensembl_assembly'
