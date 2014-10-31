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

from django.core.management.base import BaseCommand
from portal.models import Rna

####################
# Export functions #
####################

def export_fasta():
    """
    """
    for rna in Rna.objects.filter(xrefs__deleted='N', xrefs__taxid=9606).defer('seq_long').distinct().iterator():
        print rna.get_sequence_fasta()

class Command(BaseCommand):
    """
    Usage:
    python manage.py database_stats
    """

    ########################
    # Command line options #
    ########################

    # shown with -h, --help
    help = ('')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        export_fasta()
