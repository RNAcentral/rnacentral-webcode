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
from portal.models import Rna
from portal.models.rna_precomputed import RnaPrecomputed


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
        make_option(
            '--min',
            dest='min',
            type='int',
            help='Minimum RNA id to output'
        ),

        make_option(
            '--max',
            dest='max',
            type='int',
            help='Maximum RNA id to output'
        ),

        make_option(
            '--profile',
            default=False,
            action='store_true',
            help='[Optional] Show cProfile information for profiling purposes'
        ),

        make_option(
            '--upis',
            dest='upis',
            help='[Optional/Required] Comma sperated list of upis to process',
        ),

        make_option(
            '--upi-file',
            dest='upi_file',
            help='[Optional/Required] Comma sperated list of upis to process',
        ),
    )
    # shown with -h, --help
    help = ('Precompute entry data. '
            'Run `python manage.py precompute_data -h` for more information.')

    ######################
    # Django entry point #
    ######################

    def handle(self, *args, **options):
        """
        Main function, called by django.
        """

        if options['upis']:
            options['upis'] = options['upis'].split(',')
        elif options['upi_file']:
            with open(options['upi_file'], 'rb') as raw:
                options['upis'] = [line.strip() for line in raw]
        else:
            if not options['min']:
                raise CommandError('Please specify --min')

            if not options['max']:
                raise CommandError('Please specify --max')

            options['min'] = int(options['min'])
            options['max'] = int(options['max'])

        if options['profile']:
            profiler = Profile()
            profiler.runcall(self.run, options)
            profiler.print_stats()
            profiler.dump_stats('profile.txt')
        else:
            self.run(options)

    def query(self, options):
        if options['upis']:
            return Rna.objects.filter(upi__in=options['upis'])

        return Rna.objects.filter(
            id__gt=options['min'],
            id__lte=options['max'],
        )

    def run(self, options):
        sequences = self.query(options).iterator()
        for rna in sequences:
            RnaPrecomputed.objects.update_or_create(
                id=rna.upi,
                defaults={
                    'upi_id': rna.upi,
                    'rna_type': rna.get_rna_type(recompute=True),
                    'description': rna.get_description(recompute=True),
                    'rfam_problems': rna.get_rfam_status().as_json(),
                })

            for taxid in set(rna.xrefs.values_list('taxid', flat=True)):
                _id = '{0}_{1}'.format(rna.upi, taxid)
                RnaPrecomputed.objects.update_or_create(
                    id=_id,
                    defaults={
                        'upi_id': rna.upi,
                        'taxid': taxid,
                        'rna_type': rna.get_rna_type(taxid=taxid, recompute=True),
                        'description': rna.get_description(
                            recompute=True,
                            taxid=taxid,
                        ),
                        'rfam_problems': rna.get_rfam_status(taxid=taxid).as_json(),
                    })
