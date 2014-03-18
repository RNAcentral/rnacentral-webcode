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
from django.conf import settings
from portal.models import Xref, Rna
from optparse import make_option
from cProfile import Profile
from trackhub import Hub, Genomes, TrackDb
import os
import sys
import subprocess
import traceback
import cx_Oracle


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
    python manage.py export --destination /full/path/to/output/location --format track_hub --bedToBigBed /path/to/bedToBigBed
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
            help='[Required] Output format (xrefs|fasta|gff|gff3|bed|track_hub|all).'),
        make_option('-b', '--bedToBigBed',
            action='store',
            dest='bedToBigBed',
            default='',
            help='[Required for bed output] Path to bedToBigBed binary and fetchChromSizes (available from UCSC)'),
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
        self.formats     = ['xrefs', 'fasta', 'gff', 'gff3', 'bed', 'track_hub', 'all'] # available export formats
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
    # Helper functions #
    ####################
    def get_connection(self):
        """
        Get Oracle cursor using connection details from Django settings.
        """
        db_url = '{username}/{password}@{db_name}'.format(username=settings.DATABASES['default']['USER'],
                                                          password=settings.DATABASES['default']['PASSWORD'],
                                                          db_name=settings.DATABASES['default']['NAME'])
        connection = cx_Oracle.Connection(db_url)
        return connection

    def row_to_dict(self, row):
        """
        Convert Oracle results from tuples to dicts to improve code readability.
        """
        description = [d[0].lower() for d in self.cursor.description]
        return dict(zip(description,row))

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
                            all()

    def get_active_rna_sequences(self):
        """
        Get sequences with active cross-references.
        """
        return Rna.objects.only('upi', 'seq_short', 'seq_long').\
                           filter(xrefs__deleted='N').\
                           filter(xrefs__db_id=1).\
                           order_by('upi').\
                           all()

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
        rnas = self.get_active_rna_sequences()
        f = open(filename, 'w')
        upi = ''
        for rna in rnas:
            # make sure each upi is written out only once
            if rna.upi == upi:
                continue
            else:
                upi = rna.upi
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
            cmd = '. %s/fetchChromSizes %s > %s' % (self.bedToBigBed, genome, chrom_sizes_file)
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

    def export_track_hub(self, **kwargs):
        """
        Create UCSC track hub.
        """
        self.stdout.write('Exporting track hub')

        track_hub_destination = os.path.join(self.destination, 'track_hub')
        if not os.path.exists(track_hub_destination):
            os.mkdir(track_hub_destination)
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
        """
        Inspired by UniProt id mapping files.

        Output format:
        RNAcentral_id\tDatabase_name\tExternal_id

        Example:
        URS0000000161\tMIRBASE\tMIMAT0020957

        Uses the database cursor directly to improve performance.
        Django cursor seems to be ~10% slower than cx_Oracle cursor.

        Total runtime ~10 min for ~10M id mappings.
        """
        def get_accession_source():
            """
            Get a dictionary telling where to look for external database ids.
            """
            # skip 'RFAM' for now
            return {
                'xref': ['ENA'], # output xref.ac
                'external_id': ['TMRNA_WEB', 'SRPDB', 'MIRBASE', 'VEGA'], # output accession.external_id
                'optional_id': ['VEGA'], # output accession.optional_id
            }

        def process_row():
            """
            Write output for each xref.
            """
            accession_source = get_accession_source()
            result = self.row_to_dict(row)
            upi = result['upi']
            database = result['descr']
            if database in accession_source['xref']:
                line = '{upi}\t{database}\t{accession}\n'.format(upi=upi, database=database, accession=result['accession'])
                f.write(line)
            elif database in accession_source['external_id']:
                line = '{upi}\t{database}\t{accession}\n'.format(upi=upi, database=database, accession=result['external_id'])
                f.write(line)
            if database in accession_source['optional_id']:
                line = '{upi}\t{database}\t{accession}\n'.format(upi=upi, database=database, accession=result['optional_id'])
                f.write(line)

        self.stdout.write('Exporting xrefs')

        filename = self.get_output_filename('id_mapping.tsv')
        f = open(filename, 'w')

        connection = self.get_connection()
        self.cursor = connection.cursor()

        sql_cmd = """
        SELECT t1.upi, t2.ac AS accession, t3.external_id, t3.optional_id, t4.descr
        FROM rna t1, xref t2, rnc_accessions t3, rnc_database t4
        WHERE t1.upi=t2.upi AND t2.ac=t3.accession AND t2.dbid=t4.id AND t2.deleted='N'
        ORDER BY t1.upi
        """

        try:
            self.cursor.execute(sql_cmd)
            for row in self.cursor:
                process_row()
        except cx_Oracle.DatabaseError, exc:
            error, = exc.args
            raise CommandError("Oracle error code: %s\nOracle message: %s" % (error.code, error.message))

        connection.close()
        f.close()
        self.stdout.write('\tCreated file %s' % filename)
        self.gzip_file(filename)
        self.stdout.write('Xref export complete')
