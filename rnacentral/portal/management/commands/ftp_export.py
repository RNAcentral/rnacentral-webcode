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

from django.core.management.base import BaseCommand, CommandError
from portal.models import Xref, Rna
from optparse import make_option
from cProfile import Profile
from trackhub import Hub, Genomes, TrackDb
from ftp_exporters.fasta import FastaExporter
from ftp_exporters.md5 import Md5Exporter
from ftp_exporters.xrefs import XrefsExporter
import os
import re
import sys
import subprocess
import traceback


class Command(BaseCommand):
    """
    Provide a custom Django action for exporting RNAcentral data in several formats.

    Implemented in Django in order to reuse formatting routines from the RNAcentral REST API.
    Different export modes can be run in parallel.

    Usage:
    python manage.py export <options>

    Examples:
    # id mappings
    python manage.py export --destination /full/path/to/output/location --format xrefs

    # fasta
    python manage.py export --destination /full/path/to/output/location --format fasta

    # gff
    python manage.py export --destination /full/path/to/output/location --format gff

    # gff3
    python manage.py export --destination /full/path/to/output/location --format gff3

    # bed and BigBed
    python manage.py export --destination /full/path/to/output/location --format bed --bedToBigBed /path/to/bedToBigBed

    # UCSC track hub
    python manage.py export --destination /full/path/to/output/location --format track_hub

    # RNAcentral ids and their corresponding MD5s
    python manage.py export --destination /full/path/to/output/location --format md5

     # all formats
    python manage.py export --destination /full/path/to/output/location --format all --bedToBigBed /path/to/bedToBigBed

    Help:
    python manage.py export -h
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'),
        make_option('-f', '--format',
            action='store',
            dest='format',
            default=False,
            help='[Required] Output format (xrefs|fasta|gff|gff3|bed|track_hub|md5|all).'),
        make_option('-b', '--bedToBigBed',
            action='store',
            dest='bedToBigBed',
            default='',
            help='[Required for bed output] Path to bedToBigBed binary and fetchChromSizes (available from UCSC)'),
        make_option('--profile',
            default=False,
            help='[Optional] Show cProfile information for profiling purposes.'),
        make_option('--test',
            action='store',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which retrieves only a small subset of all data.'),
    )
    help = 'Export RNAcentral data in different formats. Run `python manage.py export -h` for more information.' # -h, --help

    ###########################
    # Django main entry point #
    ###########################

    def __init__(self, *args, **kwargs):
        """
        Set common variables.
        """
        super(Command, self).__init__(*args, **kwargs)
        self.formats     = ['xrefs', 'fasta', 'gff', 'gff3', 'bed', 'track_hub', 'md5', 'all'] # available export formats
        self.format      = '' # selected export format
        self.bedToBigBed = '' # path to bedToBigBed
        self.destination = '' # path to output files
        self.test        = False # when true, run on a small subset of data
        self.connection  = False # Oracle connection object
        self.cursor      = False # Oracle cursor
        self.genomes = {
            'human_hg19': 'hg19', # GRCh37
            # 'human_hg38': 'hg38', # GRCh38
            # 'mouse'     : 'mm10',
        }

    def handle(self, *args, **options):
        """
        Main function, called by django.
        """
        def _handle(self, *args, **options):
            """
            Main program. Separated from `handle` to enable Python profiling.
            """
            def set_command_line_options():
                """
                Store the command line options in the corresponding `self` variables.
                """
                cmd_options = ['bedToBigBed', 'destination', 'format', 'test']
                for cmd_option in cmd_options:
                    if options[cmd_option]:
                        setattr(self, cmd_option, options[cmd_option])

            def validate_command_line_options():
                """
                Validate the command line options.
                """
                if not self.destination:
                    raise CommandError('Please specify the --destination option')
                if not self.bedToBigBed and (options['format'] == 'bed' or options['format'] == 'all'):
                    raise CommandError('Please specify the --bedToBigBed option')
                if not self.format:
                    raise CommandError('Please specify the --format option')

            set_command_line_options()
            validate_command_line_options()
            self.export_factory(mode=self.format)

        if options['profile']:
            profiler = Profile()
            profiler.runcall(_handle, self, *args, **options)
            profiler.print_stats()
        else:
            _handle(self, *args, **options)



    ####################
    # Export functions #
    ####################

    def export_factory(self, mode):
        """
        Dynamically call the appropriate export method depending on the argument.
        """
        genome_release = self.genomes['human_hg19']

        class_name = mode.capitalize() + 'Exporter'
        constructor = globals()[class_name]
        helper = constructor(destination=self.destination, test=self.test)
        helper.start_logging()
        helper.export()

        getattr(self, 'export_%s' % mode)(genome=genome_release) # call methods like export_gff etc

    def export_all(self, **kwargs):
        """
        Export the data in all formats.
        """
        self.stdout.write('Exporting the data in all formats')
        for mode in self.formats:
            if mode == 'all':
                continue # avoid recursive calls to export_all
            self.export_factory(mode)
        self.stdout.write('Export complete')

    def export_md5(self, **kwargs):
        """
        """
        pass

    def export_fasta(self, **kwargs):
        """
        """
        pass

    def export_gff(self, **kwargs):
        pass

    def export_gff3(self, **kwargs):
        """
        Create GFF3 output files.
        Total runtime for 21K records: ~2 min
        """
        self.stdout.write('Exporting gff3')
        gff_file = self.get_output_filename('%s.gff3' % kwargs['genome'])
        f = open(gff_file, 'w')
        f.write('##gff-version 3\n')
        for xref in self.get_xrefs_with_genomic_coordinates():
            text = xref.get_gff3()
            if text:
                f.write(text)
        f.close()
        self.stdout.write('\tCreated file %s' % gff_file)
        self.gzip_file(gff_file)
        self.stdout.write('Gff3 export complete')

    def _export_big_bed(self, **kwargs):
        """
        Create BigBed output file. Called internally by export_bed().
        """
        def _set_filenames():
            """
            Set all filenames required for BED export.
            """
            return {
                'bed_sorted':   self.get_output_filename('%s.bed' % genome),
                'big_bed':      self.get_output_filename('%s.bigBed' % genome),
                'chrom_sizes':  fetch_chromosome_sizes(),
            }

        def make_big_bed():
            """
            Run bedToBigBed and produce the output.
            """
            cmd = '%s/bedToBigBed %s %s %s' % (self.bedToBigBed, files['bed_sorted'], files['chrom_sizes'], files['big_bed'])
            status = subprocess.call(cmd, shell=True)
            if status == 0:
                self.stdout.write('\tBigBed file created')
            else:
                raise CommandError('BigBed file could not be created')

        def fetch_chromosome_sizes():
            """
            Fetch chromosome sizes for a specific genome.
            """
            chrom_sizes_file = '%s.chrom.sizes' % genome
            cmd = '. %s/fetchChromSizes %s > %s' % (self.bedToBigBed, genome, chrom_sizes_file)
            status = subprocess.call(cmd, shell=True)
            if status == 0:
                self.stdout.write('\tChromosome sizes fetched')
                return chrom_sizes_file
            else:
                raise CommandError('BigBed file could not be created')

        def remove_temp_files():
            """
            Remove temporary files.
            """
            os.remove(files['chrom_sizes'])

        genome = kwargs['genome']
        files = _set_filenames()
        make_big_bed()
        remove_temp_files()

    def export_bed(self, **kwargs):
        """
        Create bed and BigBed output files.
        Total runtime for 21K records: ~14 min
        """
        def _set_filenames():
            """
            Set all filenames required for BED export.
            """
            return {
                'bed_unsorted': self.get_output_filename('%s_unsorted.bed' % genome),
                'bed_sorted':   self.get_output_filename('%s.bed' % genome),
            }

        def export_unsorted_bed_data():
            """
            Export unsorted genomic coordinates in BED format.
            """
            f = open(files['bed_unsorted'], 'w')
            for xref in self.get_xrefs_with_genomic_coordinates():
                text = xref.get_ucsc_bed()
                if text:
                    f.write(text)
            f.close()
            self.stdout.write('Exported to file "%s"' % files['bed_unsorted'])

        def bed_sort():
            """
            Sort bed file by chromosome then chromStart, as required by bedToBigBed.
            """
            cmd = "sort -k1,1 -k2,2n {0} > {1}".format(files['bed_unsorted'], files['bed_sorted'])
            status = subprocess.call(cmd, shell=True)
            if status == 0:
                self.stdout.write('\tBed file sorted')
            else:
                raise CommandError('Bed file could not be sorted')

        def remove_temp_files():
            """
            Remove temporary files.
            """
            os.remove(files['bed_unsorted'])

        def export_bed_data():
            """
            """
            self.stdout.write('Exporting bed and BigBed')
            export_unsorted_bed_data()
            bed_sort()
            remove_temp_files()
            if self.bedToBigBed:
                self._export_big_bed(**kwargs)
            self.gzip_file(files['bed_sorted'])
            self.stdout.write('Bed and BigBed export complete')

        genome = kwargs['genome']
        files = _set_filenames()
        try:
            export_bed_data()
        except:
            traceback.format_exc(sys.exc_info())
            self.stderr.write('Error: aborting Bed and BigBed export')
            return

    def export_track_hub(self, **kwargs):
        """
        Create UCSC track hub.
        """
        self.stdout.write('Exporting track hub')

        track_hub_destination = self.make_subdirectory(self.destination, 'track_hub')
        self.stdout.write('Destination: %s' % track_hub_destination)

        hub = Hub(destination=track_hub_destination)
        hub.render()

        genomes = Genomes(destination=track_hub_destination, genomes=self.genomes)
        genomes.render()

        # TODO: customize html message
        for genome in self.genomes:
            bigBed = self.get_output_filename('%s.bigBed' % self.genomes[genome])
            trackDb = TrackDb(destination=track_hub_destination, genome=self.genomes[genome], html="", bigBed=bigBed)
            trackDb.render()

        self.stdout.write('Track hub export complete')

    def export_xrefs(self, **kwargs):
        pass