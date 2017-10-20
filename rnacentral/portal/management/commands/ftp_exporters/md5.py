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

import sys

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
from portal.management.commands.common_exporters.database_connection import cursor


class Md5Exporter(FtpBase):
    """
    Export RNAcentral ids and their corresponding md5 values.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(Md5Exporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination,
                                                   self.subfolders['md5'])
        self.names = {
            'readme': 'readme.txt',
            'md5': 'md5.tsv',
            'md5_example': 'example.txt',
        }
        self.cursor = None

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

    def get_distinct_md5_sql(self):
        """
        Get RNAcentral ids and md5's of their corresponding sequences.
        """
        if self.test:
            return "SELECT * FROM rna WHERE id < %i" % self.test_entries
        else:
            return """
            SELECT DISTINCT upi, md5
            FROM rna
            ORDER BY upi
            """

    def export_md5(self):
        """
        Write out the data.
        """
        try:
            with cursor() as cur:
                cur.execute(self.get_distinct_md5_sql())
                for counter, result in enumerate(cur):
                    if self.test and counter > self.test_entries:
                        break
                    md5 = '{upi}\t{md5}\n'.format(upi=result['upi'],
                                                  md5=result['md5'])
                    self.filehandles['md5'].write(md5)
                    if counter < self.examples:
                        self.filehandles['md5_example'].write(md5)
        except Exception as exc:
            self.log_database_error(exc)
            sys.exit(1)

    def create_readme(self):
        """
        ===================================================================
        RNAcentral MD5 Data
        ===================================================================

        Each RNAcentral id corresponds to an md5 hash calculated
        based on the uppercase DNA version of that sequence.

        * md5.tsv.gz
        Tab-separated file with RNAcentral ids and md5 hashes
        of their corresponding sequences.
        This file can be used to look up RNAcentral ids for a set of sequences
        given their md5.

        * example.txt
        A small file showing the first few md5 entries.
        """
        text = self.create_readme.__doc__
        text = self.format_docstring(text)
        self.filehandles['readme'].write(text)
