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
import csv
import logging
import os
import subprocess
import sys
import traceback


class BedExporter(FtpBase):
    """
    Create bed and BigBed output files.
    """
    def __init__(self, *args, **kwargs):
        """
        Set common variables.
        """
        super(BedExporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['coordinates'])
        self.name_templates = {
            'bed_sorted': self.get_output_filename('{species}.{assembly}.bed', parent_dir=self.subdirectory),
            'bed_unsorted': self.get_output_filename('{species}.{assembly}_unsorted.bed', parent_dir=self.subdirectory),
            'big_bed': self.get_output_filename('{assembly_ucsc}.bigBed', parent_dir=self.subdirectory),
            'example': self.get_output_filename('bed_example.txt', parent_dir=self.subdirectory),
            'chrom_sizes': '', # initialize later with fetch_chromosome_sizes()
        }
        self.names = {}
        self.genome = None
        self.chrom_sizes = None
        self.bedToBigBed = ''
        self.logger = logging.getLogger(__name__)

    def fetch_chromosome_sizes(self, assembly_ucsc):
        """
        Fetch chromosome sizes for a specific genome.
        Return the name of the output file.
        """
        filename = '{assembly_ucsc}.chrom.sizes'.format(assembly_ucsc=assembly_ucsc)
        chrom_sizes_file = self.get_output_filename(filename, parent_dir=self.subdirectory)
        cmd = '. %s/fetchChromSizes %s > %s' % (self.bedToBigBed, assembly_ucsc, chrom_sizes_file)
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            self.logger.info('Chromosome sizes fetched')
            return chrom_sizes_file
        else:
            self.logger.critical(cmd)
            self.logger.critical('Chromosome sizes file was not retrieved')
            sys.exit(1)

    def parse_chrom_sizes(self):
        """
        Store chromosome sizes in a dictionary.
        """
        self.chrom_sizes = dict()
        with open(self.names['chrom_sizes'], 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.chrom_sizes[row[0]] = row[1]

    def validate_chr_names(self, bed):
        """
        Ensure that all chr names appear in the chrom.sizes file.
        """
        if not bed:
            return False
        lines = bed.split('\n')
        accepted = []
        for line in lines:
            if not line:
                continue
            words = line.split('\t')
            if words[0] not in self.chrom_sizes:
                # try with "chr"
                words[0] = 'chr' + words[0]
                if words[0] not in self.chrom_sizes:
                    return False
            accepted.append('\t'.join(words))
        return '\n'.join(accepted) + '\n'

    def export_unsorted_bed_data(self):
        """
        Export unsorted genomic coordinates in BED format.
        """
        counter = 0
        accessions = self.get_xrefs_with_genomic_coordinates(taxid=self.genome['taxid'])
        if not len(accessions):
            self.logger.info('No coordinates to export')
            return counter
        with open(self.names['bed_unsorted'], 'w') as f, \
             open(self.names['example'], 'w') as example:
            for accession in accessions:
                text = Xref.default_objects.get(accession=accession, deleted='N').get_ucsc_bed()
                if self.genome['assembly_ucsc']:
                    text = self.validate_chr_names(text)
                if text:
                    f.write(text)
                    counter += 1
                    if counter < self.examples:
                        example.write(text)
                    if self.test and counter > self.test_entries:
                        break
        self.logger.info('Exported to file "%s"' % self.names['bed_unsorted'])
        return counter

    def bed_sort(self):
        """
        Sort bed file by chromosome then chromStart, as required by bedToBigBed.
        """
        cmd = "sort -k1,1 -k2,2n {0} > {1}".format(self.names['bed_unsorted'], self.names['bed_sorted'])
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            self.logger.info('Bed file sorted')
        else:
            self.logger.critical('Bed file could not be sorted')
            sys.exit(1)

    def remove_temp_files(self):
        """
        Remove temporary files.
        """
        os.remove(self.names['bed_sorted'])
        os.remove(self.names['bed_unsorted'])
        if os.path.exists(self.names['chrom_sizes']):
            os.remove(self.names['chrom_sizes'])

    def remove_duplicate_features(self):
        """
        Bed files should contain only unique URS ids.
        The duplicates come from multiple xrefs
        pointing to the same sequence.
        """
        cmd = ('cat {input} | uniq -u > {input}_temp && ' + \
               'mv {input}_temp {input}').format(input=self.names['bed_sorted'])
        status = subprocess.call(cmd, shell=True)
        if status != 0:
            self.logger.critical('Error while removing duplicate features')
            sys.exit(1)

    def export(self, genome=None, bedToBigBed=''):
        """
        Main export function.
        """
        self.genome = genome
        self.chrom_sizes = dict()
        self.genome['species'] = self.genome['species'].replace(' ','_')
        self.bedToBigBed = bedToBigBed

        self.names = self.name_templates.copy()
        if genome['assembly_ucsc']:
            self.names['chrom_sizes'] = self.fetch_chromosome_sizes(self.genome['assembly_ucsc'])
        for key, value in self.names.iteritems():
            self.names[key] = value.format(**self.genome)

        if genome['assembly_ucsc']:
            self.parse_chrom_sizes()
        try:
            self.export_bed()
        except:
            self.logger.error(traceback.format_exc(sys.exc_info()))
            self.logger.critical('Error: aborting Bed and BigBed export')
            sys.exit(1)

    def export_bed(self):
        """
        Export the data in sorted BED format.
        """
        self.logger.info('Exporting bed and BigBed')
        exported = self.export_unsorted_bed_data()
        if not exported:
            return
        self.bed_sort()
        self.remove_duplicate_features()
        if self.bedToBigBed and self.genome['assembly_ucsc']:
            self.export_big_bed()
        self.gzip_file(self.names['bed_sorted'])
        self.remove_temp_files()
        self.logger.info('Bed and BigBed export complete')

    def export_big_bed(self):
        """
        Run bedToBigBed and produce the output.
        """
        self.logger.info(self.names['chrom_sizes'])
        cmd = '%s/bedToBigBed %s %s %s' % (self.bedToBigBed, \
            self.names['bed_sorted'], self.names['chrom_sizes'], self.names['big_bed'])
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            self.logger.info('BigBed file created')
        else:
            self.logger.critical(status)
            self.logger.critical('BigBed file could not be created')
            sys.exit(1)
