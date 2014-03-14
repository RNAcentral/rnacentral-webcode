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
import os
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
    # fasta
    python manage.py export --destination /full/path/to/output/location --format fasta
    # gff
    python manage.py export --destination /full/path/to/output/location --format gff
    # gff3
    python manage.py export --destination /full/path/to/output/location --format gff3
    # bed and BigBed
    python manage.py export --destination /full/path/to/output/location --format bed --bedToBigBed /path/to/bedToBigBed
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
            help='[Required] Output format (bed|gff|gff3|fasta|all).'),
        make_option('-b', '--bedToBigBed',
            action='store',
            dest='bedToBigBed',
            default='',
            help='[Required for bed output] Path to bedToBigBed binary and fetchChromSizes.sh (available from UCSC)'),
        make_option('--profile',
            default=False,
            help='[Optional] Show cProfile information for profiling purposes.'),
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
        self.formats     = ['gff', 'gff3', 'bed', 'fasta', 'all'] # available export formats
        self.format      = '' # selected export format
        self.bedToBigBed = '' # path to bedToBigBed
        self.destination = '' # path to output files
        self.genomes = {
            'human_hg19': 'hg19', # GRCh37
            'human_hg38': 'hg38', # GRCh38
            'mouse'     : 'mm10',
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
                cmd_options = ['bedToBigBed', 'destination', 'format']
                for cmd_option in cmd_options:
                    if options[cmd_option]:
                        setattr(self, cmd_option, options[cmd_option])

            def validate_command_line_options():
                """
                Validate the command line options.
                """
                if not self.destination:
                    raise CommandError('Please specify the --output option')
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
    # Helper functions #
    ####################

    def gzip_file(self, filename):
        """
        Compress a given file using gzip, return the compressed file name.
        """
        gzipped_filename = '%s.gz' % filename
        cmd = 'gzip < %s > %s' % (filename, gzipped_filename)
        self.stdout.write('\tCompressing file %s' % filename)
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            self.stdout.write('\tFile compressed, new file %s' % gzipped_filename)
            return gzipped_filename
        else:
            self.stdout.write('\tCompressing failed, no file created')
            return ''

    def get_output_filename(self, filename):
        """
        Generate ouput filename.
        """
        return os.path.join(self.destination, filename)

    def get_xrefs_with_genomic_coordinates(self):
        """
        Get RNA sequences with genomic coordinates.
        """
        return Xref.objects.filter(db_id=5).\
                            select_related('accession', 'accession__assembly',
                                           'accession__assembly__chromosome').\
                            all()[:100]

    ####################
    # Export functions #
    ####################

    def export_factory(self, mode):
        """
        Dynamically call the appropriate export method depending on the argument.
        """
        genome_release = self.genomes['human_hg19']
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

    def export_fasta(self, **kwargs):
        """
        Export all RNAcentral sequences in FASTA format.
        Total runtime for 6M records: ~34m
        """
        self.stdout.write('Exporting fasta')
        filename = self.get_output_filename('rnacentral.fasta')
        rnas = Rna.objects.only('upi', 'seq_short', 'seq_long').\
                           order_by('upi').\
                           all()[:1000]
        f = open(filename, 'w')
        for rna in rnas:
            f.write(rna.get_sequence_fasta())
        f.close()
        self.gzip_file(filename)
        self.stdout.write('Fasta export complete')

    def export_gff(self, **kwargs):
        """
        Create GFF output files.
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
        self.stdout.write('Gff export complete')

    def export_gff3(self, **kwargs):
        """
        Create GFF3 output files.
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
            cmd = '. %s/fetchChromSizes.sh %s > %s' % (self.bedToBigBed, genome, chrom_sizes_file)
            status = subprocess.call(cmd, shell=True)
            if status == 0:
                self.stdout.write('\tChromosome sizes fetched')
                return chrom_sizes_file
            else:
                raise CommandError('BigBed file could not be created')

        def clean_up():
            """
            Remove temporary files.
            """
            os.remove(files['chrom_sizes'])

        genome = kwargs['genome']
        files = _set_filenames()
        make_big_bed()
        clean_up()

    def export_bed(self, **kwargs):
        """
        Create bed and BigBed output files.
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

        def clean_up():
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
            clean_up()
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

    def export_track_hub(self):
        """
        """
        pass

    def export_xrefs(self):
        """
        """
        pass
