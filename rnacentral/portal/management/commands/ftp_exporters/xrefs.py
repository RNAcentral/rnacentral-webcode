"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
import cx_Oracle
import logging
import sys


class XrefsExporter(FtpBase):
    """
    Export id mappings between RNAcentral and expert databases.
    Inspired by UniProt id mapping files.

    Output format:
    RNAcentral_id\tDatabase_name\tExternal_id\tTax_id

    Example:
    URS0000000161\tMIRBASE\tMIMAT0020957\t9606

    Uses the database cursor directly to improve performance.
    Django cursor seems to be ~10% slower than cx_Oracle cursor.

    Total runtime ~10 min for ~10M id mappings.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(XrefsExporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['xrefs'])
        self.names = {
            'readme': 'readme.txt',
            'xrefs': 'id_mapping.tsv',
            'example': 'example.txt',
        }
        self.logger = logging.getLogger(__name__)

    def export(self):
        """
        Main export function.
        """
        self.setup()
        self.create_readme()
        self.export_xrefs()
        self.clean_up()
        self.logger.info('Xref export complete')

    def setup(self):
        """
        Initialize database connection and filehandles.
        """
        self.logger.info('Exporting xref data to %s' % self.subdirectory)
        self.get_filenames_and_filehandles(self.names, self.subdirectory)
        self.get_connection()
        self.get_cursor()

    def export_xrefs(self):
        """
        """
        def get_xrefs_sql():
            """
            Get SQL command for id mappings.
            """
            if self.test:
                return """
                SELECT t1.upi, t2.ac AS accession, t3.external_id, t3.optional_id, t4.descr, t2.taxid
                FROM rna t1, xref t2, rnc_accessions t3, rnc_database t4
                WHERE t1.upi=t2.upi AND t2.ac=t3.accession AND t2.dbid=t4.id AND t2.deleted='N'
                """
            return """
            SELECT t1.upi, t2.ac AS accession, t3.external_id, t3.optional_id, t4.descr, t2.taxid
            FROM rna t1, xref t2, rnc_accessions t3, rnc_database t4
            WHERE t1.upi=t2.upi AND t2.ac=t3.accession AND t2.dbid=t4.id AND t2.deleted='N'
            ORDER BY t1.upi
            """

        def get_accession_source():
            """
            Get a dictionary telling where to look for external database ids.
            """
            return {
                'xref': ['ENA'], # output xref.ac
                'optional_id': ['VEGA'], # output accession.optional_id
                # for VEGA output both transcript and gene ids
            }

        def process_xref_entries():
            """
            Write output for each xref.
            """
            counter = 0

            for row in self.cursor:
                if self.test and counter > self.test_entries:
                    return
                accession_source = get_accession_source()
                result = self.row_to_dict(row)
                upi = result['upi']
                database = result['descr']
                taxid = result['taxid']

                # use PDB instead of PDB because PDB ids come from wwPDB
                if database == 'PDBE':
                    database = 'PDB'

                if database in accession_source['xref']:
                    line = '{upi}\t{database}\t{accession}\t{taxid}\n'.format(upi=upi,
                                                                              database=database,
                                                                              accession=result['accession'],
                                                                              taxid=taxid)
                else:
                    line = '{upi}\t{database}\t{accession}\t{taxid}\n'.format(upi=upi,
                                                                              database=database,
                                                                              accession=result['external_id'],
                                                                              taxid=taxid)
                self.filehandles['xrefs'].write(line)
                if counter < self.examples:
                    self.filehandles['example'].write(line)
                # write out optional ids too, if necessary
                if database in accession_source['optional_id']:
                    line = '{upi}\t{database}\t{accession}\t{taxid}\n'.format(upi=upi,
                                                                              database=database,
                                                                              accession=result['optional_id'],
                                                                              taxid=taxid)
                    self.filehandles['xrefs'].write(line)
                counter += 1

        sql = get_xrefs_sql()
        try:
            self.cursor.execute(sql)
            process_xref_entries()
        except cx_Oracle.DatabaseError, exc:
            self.log_oracle_error(exc)
            sys.exit(1)

        self.logger.info('Xref export complete')

    def create_readme(self):
        """
        ===================================================================
        RNAcentral Id Mappings
        ===================================================================


        * id_mapping.tsv.gz
        Tab-separated file with RNAcentral ids, corresponding external ids,
        and NCBI taxon ids.

        * example.txt
        A small file showing the first few entries.
        """
        text = self.create_readme.__doc__
        text = self.format_docstring(text)
        self.filehandles['readme'].write(text)
