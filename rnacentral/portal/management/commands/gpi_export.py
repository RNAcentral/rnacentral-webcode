"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

from optparse import make_option
import os
from django.core.management.base import BaseCommand, CommandError
from common_exporters.oracle_connection import OracleConnection

"""
Export RNAcentral species-specific ids in GPI format.
The data are used for validation purposes in Protein2GO.

Usage:
python manage.py gpi_export -d /path/to/destination

To run in test mode:
python manage.py gpi_export -d /path/to/destination -t

GPI format documentation:
http://geneontology.org/page/gene-product-information-gpi-format

Example GPI file:
ftp://ftp.ebi.ac.uk/pub/databases/intact/current/various/intact_complex.gpi
"""

class GPIExporter(object):
    """
    Export RNAcentral species-specific ids in GPI format.
    """
    def __init__(self, **kwargs):
        """
        Setup file path and store command line options.
        """
        self.destination = kwargs['destination']
        self.test = kwargs['test']
        self.filename = 'rnacentral.gpi'
        self.filepath = os.path.join(self.destination, self.filename)

    def format_row(self, row):
        """
        Export a result row as a string in GPI format.
        """
        # the order of array elements defines the field order in the output
        keys = ['database', 'DB_Object_ID', 'DB_Object_Symbol',
                'DB_Object_Name', 'DB_Object_Synonym', 'DB_Object_Type',
                'Taxon', 'Parent_Object_ID', 'DB_Xref',
                'Gene_Product_Properties']
        data = dict()
        for key in keys:
            data[key] = ''
        data['database'] = 'RNAcentral'
        data['DB_Object_ID'] = '{upi}_{taxid}'.format(upi=row['upi'], taxid=row['taxid'])
        data['Taxon'] = 'taxon:{taxon}'.format(taxon=row['taxid'])
        data['DB_Object_Type'] = 'rna'
        return '\t'.join([data[key] for key in keys]) + '\n'

    def __call__(self):
        """
        Main export function.
        """
        def get_sql_command():
            """
            Get all active xrefs.
            """
            sql_cmd = """
            SELECT DISTINCT upi, taxid
            FROM xref
            WHERE deleted = 'N'
            """
            if self.test:
                sql_cmd += ' AND dbid = 5' # just Vega xrefs
            return sql_cmd

        counter = 0
        db = OracleConnection()
        db.get_cursor()
        db.cursor.execute(get_sql_command())

        with open(self.filepath, 'w') as f:
            for row in db.cursor.fetchall():
                if counter == 0:
                    f.write('!gpi-version: 1.2\n')
                f.write(self.format_row(db.row_to_dict(row)))
                counter += 1
        db.close_connection()

        assert(counter > 0)
        assert(os.path.exists(self.filepath))

        print 'Exported %i entries' % counter
        print 'File %s' % self.filepath


class Command(BaseCommand):
    """
    Handle command line options.
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'),

        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which retrieves only a small subset of all data.'),
    )
    # shown with -h, --help
    help = ('Export species-specific RNAcentral ids in GPI format')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['destination']:
            raise CommandError('Please specify --destination')

        GPIExporter(**options)()
