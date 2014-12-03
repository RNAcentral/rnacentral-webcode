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
from portal.models import RnaPrecomputedData, Rna


####################
# Import functions #
####################

def precompute_rna_data():
    """
    """
    prev_upi = ''
    for rna in Rna.objects.filter(xrefs__taxid=9606, xrefs__deleted='N').\
                           order_by('id').\
                           iterator():
        if rna.upi == prev_upi:
            continue
        else:
            prev_upi = rna.upi
        precomputed = RnaPrecomputedData.objects.filter(upi=rna).get() or RnaPrecomputedData()

        # populate or update the fields
        precomputed.upi=rna
        precomputed.description=rna.get_description()
        precomputed.count_human_xrefs=rna.count_human_xrefs()
        precomputed.count_distinct_organisms=rna.count_distinct_organisms
        precomputed.has_human_genomic_coordinates=rna.has_human_genomic_coordinates()
        precomputed.N_symbols=rna.count_symbols()['N']

        print precomputed.description
        precomputed.save()


class Command(BaseCommand):
    """
    """

    ########################
    # Command line options #
    ########################

    # shown with -h, --help
    help = ('Store precomputed annotations of RNA entries in the database.')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        precompute_rna_data()
