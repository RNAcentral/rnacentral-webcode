"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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


class Md5Exporter(FtpBase):
    """
    Export RNAcentral ids and their corresponding md5 values.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(Md5Exporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['md5'])
        self.names = {
            'readme': 'readme.txt',
            'md5': 'md5.tsv',
            'md5_example': 'example.txt',
        }
        self.logger = logging.getLogger(__name__)

    def export(self):
        """
        Main export function.
        """
        self.setup()
        self.create_readme()
        self.export_md5()
        self.clean_up()
        self.logger.info('Md5 export complete')

    def setup(self):
        """
        Initialize database connection and filehandles.
        """
        self.logger.info('Exporting md5 data to %s' % self.subdirectory)
        self.get_filenames_and_filehandles(self.names, self.subdirectory)
        self.get_connection()
        self.get_cursor()

    def export_md5(self):
        """
        Write out the data.
        """
        def get_distinct_md5_sql():
            """
            Get RNAcentral ids and md5's of their corresponding sequences.
            """
            if self.test:
                return """SELECT * FROM rna"""
            return """
            SELECT DISTINCT upi, md5
            FROM rna
            ORDER BY upi
            """

        def process_md5_entries():
            """
            Create md5.tsv and md5_example.txt files.
            """
            counter = 0
            for row in self.cursor:
                if self.test and counter > self.test_entries:
                    return
                result = self.row_to_dict(row)
                md5 = '{upi}\t{md5}\n'.format(upi=result['upi'], md5=result['md5'])
                self.filehandles['md5'].write(md5)
                if counter < self.examples:
                    self.filehandles['md5_example'].write(md5)
                counter += 1

        sql = get_distinct_md5_sql()
        try:
            self.cursor.execute(sql)
            process_md5_entries()
        except cx_Oracle.DatabaseError, exc:
            self.log_oracle_error(exc)
            sys.exit(1)

    def create_readme(self):
        """
        ===================================================================
        RNAcentral MD5 Data
        ===================================================================

        Each RNAcentral id corresponds to an md5 hash calculated
        based on the uppercase DNA version of that sequence.

        * md5.tsv.gz
        Tab-separated file with RNAcentral ids and md5 hashes of their corresponding sequences.
        This file can be used to look up RNAcentral ids for a set of sequences given their md5.

        * example.txt
        A small file showing the first few md5 entries.
        """
        text = self.create_readme.__doc__
        text = self.format_docstring(text)
        self.filehandles['readme'].write(text)
