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
from optparse import make_option
from cProfile import Profile
from portal.management.commands.ftp_exporters.fasta import FastaExporter
from portal.management.commands.ftp_exporters.md5 import Md5Exporter
from portal.management.commands.ftp_exporters.xrefs import XrefsExporter
from portal.management.commands.ftp_exporters.gff import GffExporter, Gff3Exporter
from portal.management.commands.ftp_exporters.bed import BedExporter
from portal.management.commands.ftp_exporters.trackhub import TrackhubExporter
import os


class Command(BaseCommand):
    """
    Provide a custom Django action for exporting RNAcentral data in several formats.

    Implemented in Django in order to reuse formatting routines from the RNAcentral REST API.
    Different export modes can be run in parallel.

    Usage:
    python manage.py ftp_export <options>

    Examples:
    # id mappings
    python manage.py ftp_export --destination /full/path/to/output/location --format xrefs

    # fasta
    python manage.py ftp_export --destination /full/path/to/output/location --format fasta

    # gff
    python manage.py ftp_export --destination /full/path/to/output/location --format gff

    # gff3
    python manage.py ftp_export --destination /full/path/to/output/location --format gff3

    # bed and BigBed
    python manage.py ftp_export --destination /full/path/to/output/location --format bed --bedToBigBed /path/to/bedToBigBed

    # UCSC track hub
    python manage.py ftp_export --destination /full/path/to/output/location --format trackhub

    # RNAcentral ids and their corresponding MD5s
    python manage.py ftp_export --destination /full/path/to/output/location --format md5

     # all formats
    python manage.py ftp_export --destination /full/path/to/output/location --format all --bedToBigBed /path/to/bedToBigBed

    Help:
    python manage.py ftp_export -h
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
            help='[Required] Output format (xrefs|fasta|gff|gff3|bed|trackhub|md5|all).'),

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

    ######################
    # Django entry point #
    ######################

    def __init__(self, *args, **kwargs):
        """
        Set common variables.
        """
        super(Command, self).__init__(*args, **kwargs)

        self.options = {
            'format': '', # selected export format
            'bedToBigBed': '', # path to UCSC tools, including bedToBigBed
            'destination': '', # path to output files
            'test': False, # when true, run on a small subset of data
        }
        # the formats must come in the correct execution order, e.g. `bed` should preceed `trackhub`
        self.formats = ['xrefs', 'fasta', 'gff', 'gff3', 'bed', 'trackhub', 'md5', 'all'] # available export formats
        # Add more genomes here once they are supported
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
                        self.options[cmd_option] = options[cmd_option]

            def validate_command_line_options():
                """
                Validate the command line options.
                """
                if not self.options['destination']:
                    raise CommandError('Please specify the --destination option')
                if not os.path.exists(self.options['destination']):
                    os.makedirs(self.options['destination'])
                if not self.options['bedToBigBed'] and (options['format'] == 'bed' or options['format'] == 'all'):
                    raise CommandError('Please specify the --bedToBigBed option')
                if not self.options['format']:
                    raise CommandError('Please specify the --format option')
                if self.options['format'] not in self.formats:
                    raise CommandError('Please specify correct output format. See --help for details.')

            set_command_line_options()
            validate_command_line_options()
            self.export_factory(mode=self.options['format'])

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
        Dynamically initialize the appropriate export class depending on the `mode`.
        """
        if mode == 'all':
            self.export_all()
            return

        class_name = mode.capitalize() + 'Exporter'
        constructor = globals()[class_name]
        exporter = constructor(destination=self.options['destination'], test=self.options['test'])

        if mode in ['gff', 'gff3']: # genome coordinates
            # todo: create genomic readme
            for genome in self.genomes.values():
                exporter.export(genome=genome)
        elif mode == 'bed':
            for genome in self.genomes.values():
                exporter.export(genome=genome, bedToBigBed=self.options['bedToBigBed'])
        elif mode == 'trackhub':
            exporter.export(all_genomes=self.genomes)
        else: # fasta, md5, xrefs etc
            exporter.export()

        exporter.create_release_notes_file()
        if mode in ['gff', 'gff3', 'bed', 'trackhub']:
            exporter.create_genomic_readme()

    def export_all(self, **kwargs):
        """
        Export the data in all formats.
        """
        self.stdout.write('Exporting the data in all formats')
        for mode in self.formats:
            if mode == 'all':
                continue # avoid recursive calls to export_all
            self.export_factory(mode=mode)
        self.stdout.write('Export complete')
