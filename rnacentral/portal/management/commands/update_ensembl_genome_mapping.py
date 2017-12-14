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

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from portal.models import Rna

import pymysql.cursors


def get_ensembl_connection():
    """
    Connect to the public Ensembl MySQL database.
    """
    connection = pymysql.connect(host='ensembldb.ensembl.org',
                                 user='anonymous',
                                 port=3306,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_ensembl_databases(cursor):
    """
    Get a list of all available databases.
    Return a list of the most recent core databases, for example:
        homo_sapiens_core_91_38
        mus_musculus_core_91_38
    """
    databases = defaultdict(list)
    cursor.execute("show databases")
    for result in cursor.fetchall():
        database = result['Database']
        if database.count('_') != 4 or 'mirror' in database:
            continue
        genus, species, database_type, ensembl_release, _ = database.split('_')
        ensembl_release = int(ensembl_release)
        if ensembl_release < 80:
            continue
        if database_type == 'core':
            organism = genus + ' ' + species
            databases[organism].append((ensembl_release, database))

    to_analyse = []
    # get the most recent database
    for organism, dbs in databases.iteritems():
        most_recent = max(dbs,key=lambda item:item[0])
        to_analyse.append(most_recent[1])
    return to_analyse


def get_ensembl_insdc_mapping(cursor, database):
    """
    Get a mapping between chromosome-level INSDC accessions and Ensembl names.
    Example:
        CM001500.1	10
        CM001492.1	2
    """
    mapping = []
    cursor.execute("USE %s" % database)
    sql = """
    SELECT synonym AS insdc, name AS ensembl
    FROM seq_region t1, seq_region_synonym t2, external_db t3
    WHERE
    t1.`seq_region_id` = t2.`seq_region_id`
    AND t2.external_db_id = t3.`external_db_id`
    AND t3.db_name = 'INSDC'
    AND t1.`coord_system_id` in (
        SELECT coord_system_id
        FROM coord_system
        WHERE name = 'chromosome'
        AND attrib = 'default_version'
    )
    """
    cursor.execute(sql)
    for result in cursor.fetchall():
        mapping.append({
            'insdc': result['insdc'],
            'ensembl': result['ensembl'],
        })
    return mapping


def store_mapping(mapping):
    """
    """
    for entry in mapping:
        print '"{insdc}","{ensembl}"'.format(insdc=entry['insdc'],
                                             ensembl=entry['ensembl'])


def get_ensembl_metadata(cursor, database):
    """
    Get metadata about genomic assemblies used in Ensembl.
    """
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
    	'species.scientific_name'
    )
    """
    cursor.execute(sql)
    metadata = {}
    for result in cursor.fetchall():
        metadata[result['meta_key']] = result['meta_value']
    return metadata


def store_ensembl_metadata(metadata):
    """
    """
    line = "{assembly_id}\t{assembly_full_name}\t{GCA_accession}\t{common_name}\t{taxid}".format(
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
    python manage.py update_ensembl_genome_mapping
    """
    def handle(self, *args, **options):
        """
        Main function, called by django.
        """
        connection = get_ensembl_connection()
        try:
            with connection.cursor() as cursor:
                databases = get_ensembl_databases(cursor)
                for database in databases:
                    mapping = get_ensembl_insdc_mapping(cursor, database)
                    store_mapping(mapping)
                    ensembl_metadata = get_ensembl_metadata(cursor, database)
                    store_ensembl_metadata(ensembl_metadata)
        finally:
            connection.close()
