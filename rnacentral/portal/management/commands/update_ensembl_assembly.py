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
from __future__ import print_function

from django.core.management.base import BaseCommand
from portal.models import EnsemblAssembly
from .update_ensembl_genome_mapping import get_ensembl_connection, get_ensembl_databases


example_locations = {
    'homo_sapiens': {
        'chromosome': 'X',
        'start': 73819307,
        'end': 73856333,
    },
    'mus_musculus': {
        'chromosome': 1,
        'start': 86351908,
        'end': 86352200,
    },
    'danio_rerio': {
        'chromosome': 9,
        'start': 7633910,
        'end': 7634210,
    },
    'bos_taurus': {
        'chromosome': 15,
        'start': 82197673,
        'end': 82197837,
    },
    'rattus_norvegicus': {
        'chromosome': 'X',
        'start': 118277628,
        'end': 118277850,
    },
    'felis_catus': {
        'chromosome': 'X',
        'start': 18058223,
        'end': 18058546,
    },
    'macaca_mulatta': {
        'chromosome': 1,
        'start': 146238837,
        'end': 146238946,
    },
    'pan_troglodytes': {
        'chromosome': 11,
        'start': 78369004,
        'end': 78369219,
    },
    'canis_familiaris': {
        'chromosome': 19,
        'start': 22006909,
        'end': 22007119,
    },
    'gallus_gallus': {
        'chromosome': 9,
        'start': 15676031,
        'end': 15676160,
    },
    'xenopus_tropicalis': {
        'chromosome': 'NC_006839',
        'start': 11649,
        'end': 11717,
    },
    'saccharomyces_cerevisiae': {
        'chromosome': 'XII',
        'start': 856709,
        'end': 856919,
    },
    'schizosaccharomyces_pombe': {
        'chromosome': 'I',
        'start': 540951,
        'end': 544327,
    },
    'caenorhabditis_elegans': {
        'chromosome': 'III',
        'start': 11467363,
        'end': 11467705,
    },
    'drosophila_melanogaster': {
        'chromosome': '3R',
        'start': 7474331,
        'end': 7475217,
    },
    'bombyx_mori': {
        'chromosome': 'scaf16',
        'start': 6180018,
        'end': 6180422,
    },
    'anopheles_gambiae': {
        'chromosome': '2R',
        'start': 34644956,
        'end': 34645131,
    },
    'dictyostelium_discoideum': {
        'chromosome': 2,
        'start': 7874546,
        'end': 7876498,
    },
    'plasmodium_falciparum': {
        'chromosome': 13,
        'start': 2796339,
        'end': 2798488,
    },
    'arabidopsis_thaliana': {
        'chromosome': 2,
        'start': 18819643,
        'end': 18822629,
    }
}


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

    try:
        example_location = example_locations[metadata['species.url'].lower()]
    except KeyError:
        example_location = {'chromosome': None, 'start': None, 'end': None}
    assembly = EnsemblAssembly(
        assembly_id=metadata['assembly.default'],
        assembly_full_name=metadata['assembly.name'],
        gca_accession=metadata['assembly.accession'] if 'assembly.accession' in metadata else None,
        assembly_ucsc=metadata['assembly.ucsc_alias'] if 'assembly.ucsc_alias' in metadata else None,
        common_name=metadata['species.common_name'],
        taxid=metadata['species.taxonomy_id'],
        ensembl_url=metadata['species.url'].lower(),
        division=metadata['species.division'],
        example_chromosome=example_location['chromosome'],
        example_start=example_location['start'],
        example_end=example_location['end']
    )
    assembly.save()

    line = "{assembly_id}\t{assembly_full_name}\t{GCA_accession}\t{assembly_ucsc}\t{common_name}\t{taxid}\t{ensembl_url}\t{division}\t{example_chromosome}\t{example_start}\t{example_end}".format(
        assembly_id=metadata['assembly.default'],
        assembly_full_name=metadata['assembly.name'],
        GCA_accession=metadata['assembly.accession'] if 'assembly.accession' in metadata else '',
        assembly_ucsc=metadata['assembly.ucsc_alias'] if 'assembly.ucsc_alias' in metadata else '',
        common_name=metadata['species.common_name'],
        taxid=metadata['species.taxonomy_id'],
        ensembl_url=metadata['species.url'].lower(),
        division=metadata['species.division'],
        example_chromosome=example_location['chromosome'],
        example_start=example_location['start'],
        example_end=example_location['end']
    )
    print(line)


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