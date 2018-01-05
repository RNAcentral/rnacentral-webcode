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

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from common_exporters.oracle_connection import OracleConnection
from portal.models import Xref, Modification
from portal.models.chemical_component import ChemicalComponent

"""
Import modified nucleotides from the PDBe database into RNAcentral.

Usage:
python manage.py import_pdb_modifications -d <database_url>

database_url format: username/password@hostname:port/service_name

To run in test mode:
python manage.py -t -d <database_url>
"""

class PBDModificationsImporter(OracleConnection):
    """
    Class for importing chemical modifications information from PDBe.
    """
    def __init__(self, **kwargs):
        """
        Setup file path and store command line options.
        """
        self.test = kwargs['test']
        self.db_url = kwargs['db_url']

    def import_chemical_components(self):
        """
        Import a list of all possible nucleotide modifications.
        """
        sql = """
        select
            id,
            name,
            one_letter_code
        from
            chem_comp
        where
            type_code = 'ATOMN'
            and modification_flag = 'Y'
        """
        self.cursor.execute(sql)

        components = []
        for row in self.cursor:
            result = self.row_to_dict(row)
            components.append(ChemicalComponent(
                id=result['id'],
                description=result['name'],
                one_letter_code=result['one_letter_code']
            ))
        assert(len(components) > 500)

        if not self.test:
            ChemicalComponent.objects.all().delete() # delete previously imported entries
            ChemicalComponent.objects.bulk_create(components, batch_size=100)

    def import_modified_positions(self):
        """
        * iterate over all PDB xrefs and check if any of them contain modified
        nucleotides.
        * import positions of modified nucleotides.
        Note: prepared statements for some reason don't use database indices.
        """
        sql = """
        select
            pol_seq.entry_id,
            pol_seq.entity_id,
            pol_seq.id as position,
            pol_seq.chem_comp_id,
            residue.auth_seq_id
        from
            entity_poly_seq pol_seq,
            chem_comp chem,
            residue
        where
            pol_seq.chem_comp_id = chem.id
            and chem.type_code = 'ATOMN'
            and chem.modification_flag = 'Y'
            and residue.entry_id = pol_seq.entry_id
            and residue.entity_id = pol_seq.entity_id
            and residue.id = pol_seq.id
            and pol_seq.entry_id = '{pdb_id}'
            and pol_seq.entity_id = '{entity_id}'
            and residue.auth_asym_id = '{chain_id}'
        """
        modifications = []
        xrefs = Xref.objects.select_related('accession', 'db').\
                             filter(db__descr='PDBE', deleted='N')
        i = 0
        for xref in xrefs.all():
            print(xref.accession.accession)
            pdb_id, chain_id, entity_id = xref.accession.accession.split('_')
            self.cursor.execute(sql.format(pdb_id=pdb_id.lower(),
                entity_id=entity_id, chain_id=chain_id))
            for row in self.cursor:
                result = self.row_to_dict(row)
                print(pdb_id, chain_id, entity_id, result['chem_comp_id'], result['auth_seq_id'])
                modifications.append(Modification(
                    id = i,
                    upi = xref.upi,
                    xref = xref,
                    position = result['position'],
                    author_assigned_position = result['auth_seq_id'],
                    ccd_id = pdb_id,
                    source = 'PDB',
                    modification_id = ChemicalComponent.objects.get(id=result['chem_comp_id'])
                ))
                i += 1
        if not self.test:
            Modification.objects.all().delete() # delete previously imported entries
            Modification.objects.bulk_create(modifications, batch_size=100)

    def __call__(self):
        """
        Main import function.
        """
        print('Importing data from PDBe')
        self.get_connection(self.db_url)
        self.get_cursor()
        self.import_chemical_components()
        self.import_modified_positions()
        self.close_connection()
        print('Done')


class Command(BaseCommand):
    """
    Handle command line options.
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--db',
            dest='db_url',
            default=False,
            help='[Required] PDBe database url.'),
        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which does not change the data in the database.'),
    )
    # shown with -h, --help
    help = ('Import chemical modifications information from PDBe')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['db_url']:
            raise CommandError('Please specify PDBe database url')

        PBDModificationsImporter(**options)()
