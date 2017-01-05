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

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from cProfile import Profile
from portal.management.commands.ftp_exporters.fasta import FastaExporter
from portal.management.commands.ftp_exporters.md5 import Md5Exporter
from portal.management.commands.ftp_exporters.xrefs import XrefsExporter
from portal.management.commands.ftp_exporters.gff import GffExporter, Gff3Exporter
from portal.management.commands.ftp_exporters.bed import BedExporter
from portal.management.commands.ftp_exporters.trackhub import TrackhubExporter
from portal.config.genomes import genomes
import os

"""
Exporting RNAcentral data in several formats.

Implemented in Django in order to reuse formatting routines from the RNAcentral REST API.
Different export modes can be run in parallel.

Usage:
python manage.py ftp_export <options>

Examples:

# id mappings
python manage.py ftp_export -d /full/path/to/output/location -f xrefs

# fasta
python manage.py ftp_export -d /full/path/to/output/location -f fasta

# gff
python manage.py ftp_export -d /full/path/to/output/location -f gff

# gff3
python manage.py ftp_export -d /full/path/to/output/location -f gff3

# bed and BigBed
python manage.py ftp_export -d /full/path/to/output/location -f bed -b /path/to/bedToBigBed

# UCSC track hub
python manage.py ftp_export -d /full/path/to/output/location -f trackhub

# RNAcentral ids and their corresponding MD5s
python manage.py ftp_export -d /full/path/to/output/location -f md5

 # all formats
python manage.py ftp_export -d /full/path/to/output/location -f all -b /path/to/bedToBigBed

Help:
python manage.py ftp_export -h
"""

class Exporter(object):
    """
    A wrapper object that launches data export
    in the specified format.
    """

    def __init__(self, **kwargs):
        """
        Store relevant options in `self.options`.
        """
        self.options = dict()
        for option in ['format', 'destination', 'bedToBigBed', 'test']:
            if option in kwargs:
                self.options[option] = kwargs[option]
        # ensure the destination folder exists
        if not os.path.exists(self.options['destination']):
            os.makedirs(self.options['destination'])

    def __call__(self):
        """
        Dynamically choose an appropriate export class
        depending on the export format.
        """
        class_name = self.options['format'].capitalize() + \
                     'Exporter' # e.g. GffExporter
        constructor = globals()[class_name]
        exporter = constructor(destination=self.options['destination'],
                               test=self.options['test'])

        mode = self.options['format']

        if mode in ['gff', 'gff3']: # genome coordinates
            for genome in genomes:
                exporter.export(genome=genome)
        elif mode == 'bed':
            for genome in genomes:
                exporter.export(genome=genome, bedToBigBed=self.options['bedToBigBed'])
        elif mode == 'trackhub':
            exporter.export(all_genomes=genomes)
        else: # fasta, md5, xrefs etc
            exporter.export()

        exporter.create_release_notes_file()
        if mode in ['gff', 'gff3', 'bed', 'trackhub']:
            exporter.create_genomic_readme()


class Command(BaseCommand):
    """
    Handle command line options.
    """
    # formats must be in correct execution order for the `all` parameter to work
    # e.g. `bed` should preceed `trackhub`
    formats = ['xrefs', 'fasta', 'gff', 'gff3', 'bed', 'trackhub', 'md5', 'all']

    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'),

        make_option('-f', '--format',
            action='store',
            dest='format',
            default=False,
            help='[Required] Output format (%s).' % '|'.join(formats)),

        make_option('-b', '--bedToBigBed',
            action='store',
            dest='bedToBigBed',
            default='',
            help='[Required for bed output] Path to `bedToBigBed` and `fetchChromSizes` (available from UCSC)'),

        make_option('-p', '--profile',
            action='store_true',
            default=False,
            help='[Optional] Show cProfile information for profiling purposes.'),

        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which retrieves only a small subset of all data.'),
    )
    help = 'Export RNAcentral data in various formats. ' + \
           'Run `python manage.py export -h` for more information.' # -h, --help

    def export(self, **options):
        """
        Main export.
        """
        Exporter(**options)()

    def export_all(self, **options):
        """
        Export the data in all formats.
        """
        for mode in self.formats:
            if mode == 'all':
                continue # avoid recursive calls to export_all
            self.export(**options)

    def handle(self, **options):
        """
        Django entry point.
        """
        def validate_options():
            """
            Validate command line options.
            """
            if not options['destination']:
                raise CommandError('Please specify the --destination option')

            if not options['format']:
                raise CommandError('Please specify the --format option')

            if options['format'] in ['bed', 'all'] and not options['bedToBigBed']:
                raise CommandError('Please specify the --bedToBigBed option')

            if options['format'] not in self.formats:
                raise CommandError('Please choose a valid output format (%s)' % '|'.join(self.formats))

        validate_options()

        if options['profile']:
            profiler = Profile()
            profiler.runcall(self.export, **options)
            profiler.print_stats()
            profiler.dump_stats('profile.txt')            
        elif options['format'] == 'all':
            self.export_all(**options)
        else:
            self.export(**options)
