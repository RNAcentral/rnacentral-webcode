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

from optparse import make_option
from cProfile import Profile
import os
import subprocess
import sys
import time
import hashlib

from django.core.management.base import BaseCommand, CommandError

from portal.models import Rna
from portal.management.commands.xml_exporters.rna2xml import RnaXmlExporter

LINT_CMD = 'xmllint {filepath} --schema {schema_url} --noout --stream'
SCHEMA_URL = 'http://www.ebi.ac.uk/ebisearch/XML4dbDumps.xsd'

XML_HEADER = """
<database>
<name>RNAcentral</name>
<description>a database for non-protein coding RNA sequences</description>
<release>1.0</release>
<release_date>{release_date}</release_date>
<entry_count>{entry_count}</entry_count>
<entries>
"""


def xmllint(filepath):
    """
    Run xmllint on the output file and print the resulting report.
    """
    cmd = LINT_CMD.format(filepath=filepath, schema_url=SCHEMA_URL)

    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        sys.stderr.write('ERROR: xmllint validation failed\n')
        sys.stderr.write(err.output + '\n')
        sys.stderr.write(err.cmd + '\n')
        sys.stderr.write('Return code {0}\n'.format(err.returncode))
        sys.exit(1)


def gzip_file(filepath):
    """
    Gzip output file and keep the original.
    """
    gzipped_filename = '%s.gz' % filepath
    cmd = 'gzip < %s > %s' % (filepath, gzipped_filename)
    status = subprocess.call(cmd, shell=True)
    if status == 0:
        print('File compressed, new file %s' % gzipped_filename)
    else:
        sys.stderr.write('Compressing failed, no file created\n')
        sys.exit(1)


class Command(BaseCommand):
    """
    Usage:
    python manage.py xml_export <options>

    Example:
    python manage.py xml_export --destination /full/path/to/output/location --min=1 --max=100

    Help:
    python manage.py xml_export -h
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option(
            '-d',
            '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'
        ),

        make_option(
            '--upis',
            dest='upis',
            help='[Optional/Required] Comma sperated list of upis to process',
        ),

        make_option(
            '--min',
            dest='min',
            help='[Required] Minimum RNA id to output',
        ),

        make_option(
            '--max',
            dest='max',
            type='int',
            help='[Required] Maximum RNA id to output',
        ),

        make_option(
            '--profile',
            default=False,
            action='store_true',
            help='[Optional] Show cProfile information for profiling purposes',
        ),
    )
    # shown with -h, --help
    help = ('Export RNAcentral data in xml4dbdump format for EBeye search. '
            'Run `python manage.py xml_export -h` for more information.')

    ######################
    # Django entry point #
    ######################

    def handle(self, *args, **options):
        """
        Main function, called by django.
        """

        if not options['destination']:
            raise CommandError('Please specify --destination')

        if options['upis']:
            options['upis'] = options['upis'].split(',')
        else:
            if not options['min']:
                raise CommandError('Please specify --min')
            else:
                options['min'] = int(options['min'])
            if not options['max']:
                raise CommandError('Please specify --max')
            else:
                options['max'] = int(options['max'])

        if not os.path.exists(options['destination']):
            os.makedirs(options['destination'])

        if options['profile']:
            profiler = Profile()
            profiler.runcall(self.export_data, options)
            profiler.print_stats()
            profiler.dump_stats('profile.txt')
        else:
            self.export_data(options)

    ####################
    # Export functions #
    ####################

    def export_data(self, options):
        """
        Write the data in xml4dbdumps format to the file specified
        in the --destination option.
        """

        filename = None
        query = None
        count = None
        if options['min'] is not None:
            filename = 'xml4dbdumps__{min}__{max}.xml'.format(
                min=max(options['min'], 1),
                max=options['max'],
            )
            query = Rna.objects.filter(
                id__gt=int(options['min']),
                id__lte=int(options['max']),
            )
            count = options['max'] - options['min']

        elif options['upis']:
            upis = ','.join(sorted(options['upis']))
            filename = 'xml4dbdumps__{upis}.xml'.format(
                upis=hashlib.md5(upis).hexdigest()
            )
            query = Rna.objects.filter(upi__in=options['upis'])
            count = len(options['upis'])

        else:
            raise ValueError("This should be impossible")

        filepath = os.path.join(options['destination'], filename)
        with open(filepath, 'w') as filehandle:
            filehandle.write(XML_HEADER.format(
                release_date=time.strftime("%d/%m/%Y"),
                entry_count=count,
            ))

            exporter = RnaXmlExporter()
            for rna in query.iterator():
                filehandle.write(exporter.get_xml_entry(rna))
                filehandle.flush()

            filehandle.write('</entries></database>')

        xmllint(filename)
        gzip_file(filename)
