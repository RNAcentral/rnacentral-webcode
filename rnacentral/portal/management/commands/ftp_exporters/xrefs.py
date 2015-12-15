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
    RNAcentral_id\tDatabase_name\tExternal_id\tTax_id\tRNA_type\tGene_name

    Use cx_Oracle cursor instead of Django for faster performance.
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
            sql_command = """
            SELECT t1.upi, t2.ac AS accession, t2.taxid, t3.external_id,
                t3.optional_id, t3.feature_name, t3.ncrna_class,
                t3.gene, t4.descr
            FROM rna t1,
                 xref t2,
                 rnc_accessions t3,
                 rnc_database t4
            WHERE t1.upi=t2.upi
                AND t2.ac=t3.accession
                AND t2.dbid=t4.id
                AND t2.deleted='N'
            """
            if self.test:
                sql_command += ' AND t2.dbid = 8' # small dataset for testing
            else:
                sql_command += ' ORDER BY t1.upi'
            return sql_command

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
                gene = '' if result['gene'] is None else result['gene']
                rna_type = result['feature_name'] if result['feature_name'] != 'ncRNA' else result['ncrna_class']

                # use PDB instead of PDB because PDB ids come from wwPDB
                if database == 'PDBE':
                    database = 'PDB'

                template = '{upi}\t{database}\t{accession}\t{taxid}\t{rna_type}\t{gene}\n'
                if database in accession_source['xref']:
                    line = template.format(upi=upi,
                                           database=database,
                                           accession=result['accession'],
                                           taxid=taxid,
                                           gene=gene,
                                           rna_type=rna_type)
                else:
                    line = template.format(upi=upi,
                                           database=database,
                                           accession=result['external_id'],
                                           taxid=taxid,
                                           gene=gene,
                                           rna_type=rna_type)
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
        NCBI taxon ids, RNA types (according to INSDC classification), and gene names.

        * example.txt
        A small file showing the first few entries.

        CHANGELOG:

        * December 11, 2015
        Added two new fields: RNA type and gene name.
        """
        text = self.create_readme.__doc__
        text = self.format_docstring(text)
        self.filehandles['readme'].write(text)
