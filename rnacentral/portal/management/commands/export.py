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
import subprocess
from cProfile import Profile
import os


class Command(BaseCommand):
    """
    Provide manage.py custom action for exporting RNAcentral data
    in several formats.

    Implemented in Django in order to reuse formatting routines from the REST API.
    Can be run on a cluster using eHive for parallelization.

    Usage:
    python manage.py export --format fasta
    python manage.py export --format gff
    python manage.py export --format gff3
    python manage.py export --format bed --bedToBigBed=/path/to/bedToBigBed # also outputs BigBed
    python manage.py export --bedToBigBed=/path/to/bedToBigBed # all formats
    """

    help = 'Export RNAcentral data in various formats' # show with --help command line option
    option_list = BaseCommand.option_list + ( # add command line options
        make_option('--bedToBigBed',
            action='store',
            dest='bedToBigBed',
            default='',
            help='Path to bedToBigBed binary and fetchChromSizes.sh'),
        make_option('--format',
            action='store',
            dest='format',
            default=False,
            help='Output format (gff|gff3|bed|fasta). Omit for output in all formats.'),
        make_option('--profile',
            default=False,
            help='Show cProfile information'),
        )

    def __init__(self, *args, **kwargs):
        """
        """
        super(Command, self).__init__(*args, **kwargs)
        self.genomes = {
            'human': 'hg19',
            'mouse': 'mm10',
        }

    def handle(self, *args, **options):
        """
        Main function called by django.
        """
        if options['profile']:
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)
            profiler.print_stats()
        else:
            self._handle(*args, **options)

    def _handle(self, *args, **options):
        """
        Main program. Separated from `handle` to enable Python profiling.
        """

        def _bedToBigBed_option_is_ok():
            """
            Make sure that --bedToBigBed has been specified.
            """
            if not options['bedToBigBed']:
                self.stderr.write('Specify path to bedToBigBed binary and fetchChromSizes.sh using --bedToBigBed')
                return False
            else:
                self.bedToBigBed = options['bedToBigBed']
                return True

        if not options['format']:
            self.export_everything()
        elif options['format'] == 'gff':
            self.export_gff(self.genomes['human'])
        elif options['format'] == 'gff3':
            self.export_gff3(self.genomes['human'])
        elif options['format'] == 'bed':
            if _bedToBigBed_option_is_ok():
                self.export_bed(self.genomes['human'])
        elif options['format'] == 'fasta':
            self.export_fasta()
        else:
            self.stderr.write('Incorrect output format')

    def get_vega_xrefs(self):
        """
        Get RNA sequences for output.
        """
        return Xref.objects.filter(db_id=5).select_related('accession', 'accession__assembly', 'accession__assembly__chromosome').all()

    def gzip_file(self, filename):
        """
        Compress a given file using gzip, return the compressed file name.
        """
        gzipped_filename = '%s.gz' % filename
        cmd = 'gzip < %s > %s' % (filename, gzipped_filename)
        subprocess.call(cmd, shell=True)
        self.stdout.write('File %s gzipped into %s' % (filename, gzipped_filename))
        return gzipped_filename

    def export_everything(self):
        """
        Export all data in all formats.
        """
        self.export_gff(self.genomes['human'])
        self.export_gff3(self.genomes['human'])
        if _bedToBigBed_option_is_ok():
            self.export_bed(self.genomes['human'])
        self.export_fasta()

    def export_fasta(self):
        """
        Export all RNAcentral sequences in FASTA format.
        Total runtime for 6M records: ~34m
        """
        filename = 'rnacentral.fasta'
        rnas = Rna.objects.only('upi', 'seq_short', 'seq_long').\
                           order_by('upi').\
                           iterator()
        f = open(filename, 'w')
        for rna in rnas:
            f.write(rna.get_sequence_fasta())
        f.close()
        self.gzip_file(filename)
        self.stdout.write('Fasta export complete')

    def export_bed(self, genome):
        """
        Create BED and BIG BED output files.
        """
        def _set_filenames():
            """
            Set all filenames required for BED export.
            """
            return {
                'bed_unsorted': '%s_unsorted.bed' % genome,
                'bed_sorted': '%s.bed' % genome,
                'big_bed': '%s.bigBed' % genome,
                'chrom_sizes': _fetch_chromosome_sizes(),
            }

        def _export_unsorted_bed_data():
            """
            Export unsorted genomic coordinates in BED format.
            """
            f = open(files['bed_unsorted'], 'w')
            for xref in self.get_vega_xrefs():
                text = xref.get_ucsc_bed()
                if text:
                    f.write(text)
            f.close()
            self.stdout.write('Exported to file "%s"' % files['bed_unsorted'])

        def _bed_sort():
            """
            Sort bed file by chromosome then chromStart, as required by bedToBigBed.
            """
            cmd = "sort -k1,1 -k2,2n {0} > {1}".format(files['bed_unsorted'], files['bed_sorted'])
            subprocess.call(cmd, shell=True)
            self.stdout.write('Bed file sorted')

        def _make_big_bed():
            """
            Run bedToBigBed and produce the output.
            """
            cmd = '%s/bedToBigBed %s %s %s' % (self.bedToBigBed, files['bed_sorted'], files['chrom_sizes'], files['big_bed'])
            subprocess.call(cmd, shell=True)
            self.stdout.write('BigBed file created')

        def _fetch_chromosome_sizes():
            """
            Fetch chromosome sizes for a specific genome.
            """
            chrom_sizes_file = '%s.chrom.sizes' % genome
            cmd = '. %s/fetchChromSizes.sh %s > %s' % (self.bedToBigBed, genome, chrom_sizes_file)
            subprocess.call(cmd, shell=True)
            self.stdout.write('Chromosome sizes fetched')
            return chrom_sizes_file

        def _clean_up():
            """
            Remove temporary files.
            """
            os.remove(files['bed_unsorted'])
            os.remove(files['chrom_sizes'])

        files = _set_filenames()
        _export_unsorted_bed_data()
        _bed_sort()
        _make_big_bed()
        _clean_up()

    def export_gff(self, genome):
        """
        Create GFF output files.
        """
        gff_file = '%s.gff' % genome
        f = open(gff_file, 'w')
        for xref in self.get_vega_xrefs():
            text = xref.get_gff()
            if text:
                f.write(text)
        f.close()
        self.stdout.write('Exported to file "%s"' % gff_file)

    def export_gff3(self, genome):
        """
        Create GFF3 output files.
        """
        gff_file = '%s.gff3' % genome
        f = open(gff_file, 'w')
        f.write('##gff-version 3\n')
        for xref in self.get_vega_xrefs():
            text = xref.get_gff3()
            if text:
                f.write(text)
        f.close()
        self.stdout.write('Exported to file "%s"' % gff_file)
