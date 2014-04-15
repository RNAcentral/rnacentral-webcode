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
from django.template.loader import render_to_string
from optparse import make_option
from cProfile import Profile
import os
import time
from portal.models import Rna


class Command(BaseCommand):
    """

    Usage:
    python manage.py xml4dbdumps <options>

    Example:
    python manage.py xml4dbdumps --destination /full/path/to/output/location

    Help:
    python manage.py xml4dbdumps -h
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'),

        make_option('--profile',
            default=False,
            help='[Optional] Show cProfile information for profiling purposes'),

        make_option('--test',
            action='store',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which retrieves '
                 'only a small subset of all data'),
    )
    # shown with -h, --help
    help = ('Export RNAcentral data in xml4dbdump format for EBeye search. '
           'Run `python manage.py export -h` for more information.')

    ######################
    # Django entry point #
    ######################

    def __init__(self, *args, **kwargs):
        """
        Set common variables.
        """
        super(Command, self).__init__(*args, **kwargs)

        self.filename = 'xml4dbdumps.xml'
        self.options = {
            'destination': '',
            'test': False,
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
                cmd_options = ['destination', 'test']
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

            set_command_line_options()
            validate_command_line_options()
            self.export_data()

        if options['profile']:
            profiler = Profile()
            profiler.runcall(_handle, self, *args, **options)
            profiler.print_stats()
        else:
            _handle(self, *args, **options)

    ####################
    # Export functions #
    ####################

    def export_data(self):
        """
        Write the data in xml4dbdumps format to the file specified
        in the --destination option.
        """
        def write_xml_header():
            """
            Write out the beginning of the xml file.
            """
            database = {
                'release': '1beta',
                'release_date': time.strftime("%d/%m/%Y"),
                'entry_count': Rna.objects.count(),
            }
            f.write(render_to_string('portal/xml4dbdumps/header.xml', database))

        def write_rna_entries():
            """
            Write out RNA entries.
            """
            def get_rna_data():
                """
                Get either an efficient Django iterator for all RNA entries or
                a small subset of entries for testing mode.
                """
                if self.options['test']:
                    data = Rna.objects.all()[:100]
                else:
                    data = Rna.objects.iterator()
                return data

            for rna in get_rna_data():
                f.write(render_to_string('portal/xml4dbdumps/entry.xml',
                        {'rna': rna}))
                f.flush()

        def write_xml_footer():
            """
            Write out the end of the xml file.
            """
            f.write(render_to_string('portal/xml4dbdumps/footer.xml'))

        f = open(os.path.join(self.options['destination'], self.filename), 'w')
        write_xml_header()
        write_rna_entries()
        write_xml_footer()
        f.close()
