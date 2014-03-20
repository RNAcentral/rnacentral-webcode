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
from portal.models import Xref
import cx_Oracle
import logging
import sys


class GffExporter(FtpBase):
    """
    Create GFF output files.
    Total runtime for 21K records: ~2 min
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(GffExporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, 'genome_coordinates')
        self.names = {
            'readme': 'readme.txt',
            'gff': 'md5.tsv', #genome
            'example': 'example.txt',
        }
        self.log = 'gff_log.txt'

    def export(self):
        """
        Main export function.
        """
        self.stdout.write('Exporting gff')
        gff_file = self.get_output_filename('%s.gff' % kwargs['genome'])
        f = open(gff_file, 'w')
        for xref in self.get_xrefs_with_genomic_coordinates():
            text = xref.get_gff()
            if text:
                f.write(text)
        f.close()
        self.stdout.write('\tCreated file %s' % gff_file)
        self.gzip_file(gff_file)
        logging.info('Gff export complete')
