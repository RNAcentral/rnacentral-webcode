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

from collections import defaultdict

from django.core.management.base import BaseCommand
from portal.models import EnsemblAssembly, EnsemblInsdcMapping
from .update_ensembl_genome_mapping import get_ensembl_connection, get_ensembl_databases

import pymysql.cursors


def get_ensembl_metadata(cursor, database):
    """Get metadata about genomic assemblies used in Ensembl."""
    cursor.execute("USE %s" % database)
    sql = """
    SELECT meta_key, meta_value
    FROM meta
    WHERE meta_key IN (
    	'assembly.accession',
    	'assembly.default',
    	'assembly.long_name',
    	'assembly.name',
    	'assembly.ucsc_alias',
    	'species.division',
    	'species.production_name',
    	'species.taxonomy_id',
    	'species.common_name',
    	'species.scientific_name',
        'species.url',
        'species.division'
    )
    """
    cursor.execute(sql)
    metadata = {}
    for result in cursor.fetchall():
        metadata[result['meta_key']] = result['meta_value']
    return metadata


def store_ensembl_metadata(metadata):
    """
    Delete existing Ensembl assembly for
    the same NCBI taxid and create a new one.
    """
    EnsemblAssembly.objects.filter(taxid=metadata['species.taxonomy_id']).delete()
    assembly = EnsemblAssembly(
        assembly_id=metadata['assembly.default'],
        assembly_full_name=metadata['assembly.name'],
        gca_accession=metadata['assembly.accession'] if 'assembly.accession' in metadata else None,
        assembly_ucsc=metadata['assembly.ucsc_alias'] if 'assembly.ucsc_alias' in metadata else None,
        common_name=metadata['species.common_name'],
        taxid=metadata['species.taxonomy_id'],
        ensembl_url=metadata['species.url'],
        division=metadata['species.division'],
    )
    assembly.save()

    line = "{assembly_id}\t{assembly_full_name}\t{GCA_accession}\t{assembly_ucsc}\t{common_name}\t{taxid}".format(
        assembly_id=metadata['assembly.default'],
        GCA_accession=metadata['assembly.accession'] if 'assembly.accession' in metadata else '',
        assembly_full_name=metadata['assembly.name'],
        assembly_ucsc=metadata['assembly.ucsc_alias'] if 'assembly.ucsc_alias' in metadata else '',
        division=metadata['species.division'],
        taxid=metadata['species.taxonomy_id'],
        common_name=metadata['species.common_name'],
    )
    print line


class Command(BaseCommand):
    """
    Usage:
    python manage.py update_ensembl_assembly
    """
    def handle(self, *args, **options):
        """Main function, called by django."""
        connection = get_ensembl_connection()
        try:
            with connection.cursor() as cursor:
                databases = get_ensembl_databases(cursor)
                for database in databases:
                    ensembl_metadata = get_ensembl_metadata(cursor, database)
                    store_ensembl_metadata(ensembl_metadata)
        finally:
            connection.close()