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

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
from portal.models import Rna
import cx_Oracle
import logging
import re
import sys


def read_lob(lob):
    """
    If lob is an Oracle lob object, return its string representation.
    Otherwise, return None.
    """
    return lob.read() if lob else lob


class FastaExporter(FtpBase):
    """
    Export RNAcentral sequences in FASTA format.

    Manually create Django model instances from raw cx_Oracle results
    in order to reuse the fasta formatting routine defined on the Rna model.

    Total runtime for 6M records: ~35m
    This step is slow because of LOBs and gzipping the output file.
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(FastaExporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['sequences'])
        self.names = {
            'readme': 'readme.txt',
            'seq_active': 'rnacentral_active.fasta',
            'seq_inactive': 'rnacentral_inactive.fasta',
            'nhmmer_db': 'rnacentral_nhmmer.fasta',
            'nhmmer_db_excluded': 'rnacentral_nhmmer_excluded.fasta',
            'seq_example': 'example.txt',
        }
        self.logger = logging.getLogger(__name__)

    def export(self):
        """
        Main export function.
        """
        self.setup()
        self.create_readme()
        self.export_active_sequences()
        self.export_inactive_sequences()
        self.clean_up()
        self.logger.info('Fasta export complete')

    def setup(self):
        """
        Initialize database connection and filehandles.
        """
        self.logger.info('Exporting fasta to %s' % self.subdirectory)
        self.get_filenames_and_filehandles(self.names, self.subdirectory)
        self.get_connection()
        self.get_cursor()

    def export_active_sequences(self):
        """
        Export RNA sequences with active cross-references.
        """
        def get_active_sequences_sql():
            """
            Get sequences with at least one active cross-reference.
            """
            if self.test:
                return """SELECT * from RNA"""
            return """
            SELECT t1.upi, t1.seq_short, t1.seq_long
            FROM rna t1, xref t2
            WHERE t1.upi=t2.upi AND t2.deleted='N'
            ORDER BY t1.upi
            """

        def process_active_sequences():
            """
            Create the active.fasta file and the example.fasta file.
            """
            counter = 0
            previous_upi = ''
            valid_chars = re.compile('^[ABCDGHKMNRSTVWXYU]+$', re.IGNORECASE) # IUPAC

            for row in self.cursor:
                if self.test and counter >= self.test_entries:
                    return
                result = self.row_to_dict(row)
                if result['upi'] == previous_upi:
                    continue
                else:
                    previous_upi = result['upi']
                rna = Rna(upi=result['upi'],
                          seq_short=result['seq_short'],
                          seq_long=read_lob(result['seq_long']))
                fasta = rna.get_sequence_fasta()
                self.filehandles['seq_active'].write(fasta)
                if counter < self.examples:
                    self.filehandles['seq_example'].write(fasta)
                if valid_chars.match(rna.get_sequence()):
                    self.filehandles['nhmmer_db'].write(fasta)
                else:
                    self.filehandles['nhmmer_db_excluded'].write(fasta)
                counter += 1

        sql = get_active_sequences_sql()
        try:
            self.cursor.execute(sql)
            process_active_sequences()
        except cx_Oracle.DatabaseError, exc:
            self.log_oracle_error(exc)
            sys.exit(1)

    def export_inactive_sequences(self):
        """
        Export RNA sequences without active cross-references.
        """
        def get_inactive_sequences_sql():
            """
            Get sequences with no active cross-references.
            """
            if self.test:
                return """SELECT * from RNA"""
            return """
            SELECT t1.upi, t1.seq_short, t1.seq_long
            FROM rna t1, xref t2
            WHERE t1.upi = t2.upi AND t2.deleted = 'Y' AND t2.upi NOT IN
                (SELECT upi FROM xref WHERE deleted='N')
            ORDER BY t1.upi
            """

        def process_inactive_sequences():
            """
            Create inactive.fasta file.
            """
            counter = 0
            previous_upi = ''

            for row in self.cursor:
                if self.test and counter > self.test_entries:
                    return
                result = self.row_to_dict(row)
                if result['upi'] == previous_upi:
                    continue
                else:
                    previous_upi = result['upi']
                rna = Rna(upi=result['upi'],
                          seq_short=result['seq_short'],
                          seq_long=read_lob(result['seq_long']))
                fasta = rna.get_sequence_fasta()
                self.filehandles['seq_inactive'].write(fasta)
                counter += 1

        sql = get_inactive_sequences_sql()
        try:
            self.cursor.execute(sql)
            process_inactive_sequences()
        except cx_Oracle.DatabaseError, exc:
            self.log_oracle_error(exc)
            sys.exit(1)

    def create_readme(self):
        """
        ===================================================================
        RNAcentral Sequence Data
        ===================================================================

        This directory contains sequences with RNAcentral ids in FASTA format.

        * rnacentral_active.fasta.gz
        Current set of sequences that are present in at least one expert database.

        * rnacentral_inactive.fasta.gz
        All RNAcentral sequences that used to be present in one or more expert database
        but don't have any current cross-references.

        * example.txt
        A small example file showing the format of rnacentral_active.fasta.gz
        and rnacentral_inactive.fasta.gz.
        """
        text = self.create_readme.__doc__
        text = self.format_docstring(text)
        self.filehandles['readme'].write(text)
