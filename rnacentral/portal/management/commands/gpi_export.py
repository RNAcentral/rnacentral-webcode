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

from optparse import make_option
import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from common_exporters.oracle_connection import OracleConnection
from portal.models import Rna
from portal.utils import so_terms

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

def gzip_file(filename):
    """
    Compress a given file using gzip, return the compressed file name.
    """
    gzipped_filename = '%s.gz' % filename
    cmd = 'gzip < %s > %s' % (filename, gzipped_filename)
    print 'Compressing file %s' % filename
    status = subprocess.call(cmd, shell=True)
    if status == 0:
        print 'File compressed, new file %s' % gzipped_filename
        return gzipped_filename
    else:
        print 'Compressing failed, no file created'
        return ''


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

    def get_mirna_precursors(self, rna, taxid):
        """
        Get miRNA precursors from miRBase for mature miRNAs.
        """
        text = ''
        query = rna.xrefs.filter(db__id=4, taxid=taxid, accession__ncrna_class='miRNA')
        if query.exists():
            precursors = []
            for xref in query.all():
                precursors.append(xref.get_mirbase_precursor())
            if precursors:
                precursors = ['{upi}_{taxid}'.format(upi=x, taxid=taxid) for x in precursors if x is not None]
                precursors = set(precursors)
                text = 'precursor_rna:' + ','.join(precursors)
        return text

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
        rna = Rna(upi=row['upi'])
        data['database'] = 'RNAcentral'
        data['DB_Object_Name'] = rna.get_description(taxid=row['taxid'])
        data['DB_Object_ID'] = '{upi}_{taxid}'.format(upi=row['upi'], taxid=row['taxid'])
        data['Taxon'] = 'taxon:{taxon}'.format(taxon=row['taxid'])
        data['DB_Object_Type'] = so_terms.get_label(rna)
        data['Gene_Product_Properties'] = self.get_mirna_precursors(taxid=row['taxid'], rna=rna)

        # safeguard against breaking tsv format
        for key in keys:
            data[key] = data[key].replace('\t',' ')
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
                sql_cmd += ' AND dbid = 4 AND taxid = 9606' # human miRBase
            return sql_cmd

        def test_unique_ids():
            """
            Test uniqueness of URS_taxid identifiers.
            """
            number_of_lines = subprocess.check_output(
                ['cat %s | wc -l' % self.filepath],
                shell=True).strip()
            number_of_unique_ids = subprocess.check_output(
                ["sort -u -t$'\t' -k2,2 %s | wc -l" % self.filepath],
                shell=True).strip()
            assert(number_of_lines == number_of_unique_ids)

        def test_none_taxids():
            """
            Test that there are no None taxids
            """
            none_taxids = subprocess.check_output(
                ['grep _None %s | wc -l' % self.filepath],
                shell=True).strip()
            assert(int(none_taxids) == 0)

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

        test_unique_ids()
        test_none_taxids()

        gzip_file(self.filepath)
        print 'Exported %i entries' % counter


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
