"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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
from portal.models import Rna, RnaPrecomputed


class Command(BaseCommand):
    """
    Usage:
    python manage.py precompute_descriptions <options>

    Example:
    python manage.py precompute_descriptions --min=0 --max=100

    Help:
    python manage.py precompute_descriptions -h
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option('--min',
            dest='min',
            type='int',
            help='Minimum RNA id to output'),

        make_option('--max',
            dest='max',
            type='int',
            help='Maximum RNA id to output'),

        make_option('--profile',
            default=False,
            action='store_true',
            help='[Optional] Show cProfile information for profiling purposes'),
    )
    # shown with -h, --help
    help = ('Precompute entry descriptions. '
            'Run `python manage.py precompute_descriptions -h` for more information.')

    ######################
    # Django entry point #
    ######################

    def __init__(self, *args, **kwargs):
        """
        Set common variables.
        """
        super(Command, self).__init__(*args, **kwargs)
        self.options = {
            'min': 10,
            'max': 100,
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
                Store command line options in `self.options`.
                """
                cmd_options = ['min', 'max']
                for cmd_option in cmd_options:
                    if options[cmd_option]:
                        self.options[cmd_option] = str(options[cmd_option])

            def validate_command_line_options():
                """
                Validate the command line options.
                """
                if not self.options['min']:
                    raise CommandError('Please specify --min')
                if not self.options['max']:
                    raise CommandError('Please specify --max')

            set_command_line_options()
            validate_command_line_options()
            self.run()

        if options['profile']:
            profiler = Profile()
            profiler.runcall(_handle, self, *args, **options)
            profiler.print_stats()
            profiler.dump_stats('profile.txt')
        else:
            _handle(self, *args, **options)

    def run(self):
        """
        """
        for rna in Rna.objects.filter(id__gt=self.options['min'],
                                      id__lte=self.options['max']).iterator():
            defaults = {
                'upi_id': rna.upi,
                'description': rna.get_description(recompute=True),
            }
            RnaPrecomputed.objects.update_or_create(id=rna.upi, defaults=defaults)

            for taxid in set(rna.xrefs.values_list('taxid', flat=True)):
                _id = '{0}_{1}'.format(rna.upi, taxid)
                defaults = {
                    'description': rna.get_description(recompute=True, taxid=taxid),
                    'upi_id': rna.upi,
                    'taxid': taxid,
                }
                RnaPrecomputed.objects.update_or_create(id=_id, defaults=defaults)
