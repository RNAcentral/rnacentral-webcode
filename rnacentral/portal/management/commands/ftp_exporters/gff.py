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

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
from portal.models import Xref
import logging
import os


class GffExporter(FtpBase):
    """
    Create GFF output files.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(GffExporter, self).__init__(*args, **kwargs)
        self.subdirectory = self.make_subdirectory(self.destination,
                                                   self.subfolders['coordinates'])

    def export(self, genome):
        """
        Main export function.
        """
        self.logger.info('Exporting gff')
        filename = '%s.%s.gff' % (genome['species'].replace(' ', '_'),
                                  genome['assembly'])
        gff_file = self.get_output_filename(filename,
                                            parent_dir=self.subdirectory)
        example_file = self.get_output_filename('gff_example.txt',
                                                parent_dir=self.subdirectory)
        f = open(gff_file, 'w')
        example = open(example_file, 'w')
        counter = 0
        taxid = genome['taxid']
        self.logger.info('Exporting data for %s', genome['species'])
        accessions = self.get_xrefs_with_genomic_coordinates(taxid)
        for accession in accessions:
            text = Xref.default_objects.get(accession=accession, deleted='N').get_gff()
            if text:
                f.write(text)
                counter += 1
                if counter < self.examples:
                    example.write(text)
                if self.test and counter > self.test_entries:
                    break
        f.close()
        example.close()
        self.logger.info('Created file %s' % gff_file)
        self.gzip_file(gff_file)
        os.remove(gff_file)
        self.logger.info('Gff export complete')


class Gff3Exporter(FtpBase):
    """
    Create GFF3 output files.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(Gff3Exporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['coordinates'])
        self.logger = logging.getLogger(__name__)

    def export(self, genome):
        """
        Main export function.
        """
        self.logger.info('Exporting gff3')
        filename = '%s.%s.gff3' % (genome['species'].replace(' ', '_'), genome['assembly'])
        gff_file = self.get_output_filename(filename, parent_dir=self.subdirectory)
        example_file = self.get_output_filename('gff3_example.txt',
                                                parent_dir=self.subdirectory)
        self.logger.info('Exporting data for %s', genome['species'])
        f = open(gff_file, 'w')
        example = open(example_file, 'w')
        header = '##gff-version 3\n'
        f.write(header)
        example.write(header)
        counter = 0
        for accession in self.get_xrefs_with_genomic_coordinates(taxid=genome['taxid']):
            text = Xref.default_objects.get(accession=accession, deleted='N').get_gff3()
            if text:
                f.write(text)
                counter += 1
                if counter < self.examples:
                    example.write(text)
                if self.test and counter > self.test_entries:
                    break
        f.close()
        example.close()
        self.logger.info('Created file %s' % gff_file)
        self.gzip_file(gff_file)
        os.remove(gff_file)
        self.logger.info('Gff3 export complete')
