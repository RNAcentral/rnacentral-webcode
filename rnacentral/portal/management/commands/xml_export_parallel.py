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
from django.db.models import Max
from optparse import make_option
from portal.models import Rna


class Command(BaseCommand):
    """
    Usage:
    python manage.py xml_export_parallel --destination /full/path/to/output/location

    Help:
    python manage.py xml_export_parallel -h
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
            default='',
            dest='destination',
            help='[Required] Full path to the output directory'),
    )
    # shown with -h, --help
    help = ('Create LSF commands for parallelizing xml export.')

    ######################
    # Django entry point #
    ######################

    def handle(self, *args, **options):
        """
        Main function, called by django.
        """
        if not options['destination']:
            raise CommandError('Please specify --destination')

        total = Rna.objects.all().aggregate(Max('id'))['id__max']
        step = pow(10, 5) * 2
        start = 0
        stop = 0

        for i in xrange(step, total, step):
            start = stop
            stop = min(total, i)
            print get_lsf_command(start, stop, options['destination'])

        if stop < total:
            start = stop
            stop = total
            print get_lsf_command(start, stop, options['destination'])


def get_lsf_command(start, stop, destination):
    """
    Get LSF command.
    """
    return ('bsub '
                '-o output__{0}__{1}.txt '
                '-e errors__{0}__{1}.txt '
            'python manage.py xml_export '
                '--min {0} '
                '--max {1} '
                '-d {2}').format(start, stop, destination)
