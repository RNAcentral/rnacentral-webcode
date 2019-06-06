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
from __future__ import print_function

from django.core.management.base import BaseCommand
from portal.models import EnsemblAssembly
from portal.models import SequenceRegion


example_locations = {
    'homo_sapiens': {
        'chromosome': 'X',
        'start': 73819307,
        'end': 73856333,
    },
    'mus_musculus': {
        'chromosome': 1,
        'start': 86351908,
        'end': 86352200,
    },
    'danio_rerio': {
        'chromosome': 9,
        'start': 7633910,
        'end': 7634210,
    },
    'bos_taurus': {
        'chromosome': 15,
        'start': 82197673,
        'end': 82197837,
    },
    'rattus_norvegicus': {
        'chromosome': 'X',
        'start': 118277628,
        'end': 118277850,
    },
    'felis_catus': {
        'chromosome': 'X',
        'start': 18058223,
        'end': 18058546,
    },
    'macaca_mulatta': {
        'chromosome': 1,
        'start': 146238837,
        'end': 146238946,
    },
    'pan_troglodytes': {
        'chromosome': 11,
        'start': 78369004,
        'end': 78369219,
    },
    'canis_familiaris': {
        'chromosome': 19,
        'start': 22006909,
        'end': 22007119,
    },
    'gallus_gallus': {
        'chromosome': 9,
        'start': 15676031,
        'end': 15676160,
    },
    'xenopus_tropicalis': {
        'chromosome': 'NC_006839',
        'start': 11649,
        'end': 11717,
    },
    'saccharomyces_cerevisiae': {
        'chromosome': 'XII',
        'start': 856709,
        'end': 856919,
    },
    'schizosaccharomyces_pombe': {
        'chromosome': 'I',
        'start': 540951,
        'end': 544327,
    },
    'triticum_aestivum': {
        'chromosome': '6A',
        'start': 100656614,
        'end': 	100656828,
    },
    'caenorhabditis_elegans': {
        'chromosome': 'III',
        'start': 11467363,
        'end': 11467705,
    },
    'drosophila_melanogaster': {
        'chromosome': '3R',
        'start': 7474331,
        'end': 7475217,
    },
    'bombyx_mori': {
        'chromosome': 'scaf16',
        'start': 6180018,
        'end': 6180422,
    },
    'anopheles_gambiae': {
        'chromosome': '2R',
        'start': 34644956,
        'end': 34645131,
    },
    'dictyostelium_discoideum': {
        'chromosome': 2,
        'start': 7874546,
        'end': 7876498,
    },
    'plasmodium_falciparum': {
        'chromosome': 13,
        'start': 2796339,
        'end': 2798488,
    },
    'arabidopsis_thaliana': {
        'chromosome': 2,
        'start': 18819643,
        'end': 18822629,
    }
}

def update_example_locations():
    """
    """
    for assembly in EnsemblAssembly.objects.filter(division__in=['EnsemblVertebrates', 'EnsemblPlants']).all():
        print(assembly.ensembl_url)
        if assembly.ensembl_url in example_locations:
            assembly.example_chromosome = example_locations[assembly.ensembl_url]['chromosome']
            assembly.example_start = example_locations[assembly.ensembl_url]['start']
            assembly.example_end = example_locations[assembly.ensembl_url]['end']
            assembly.save()
            continue
        try:
            region = SequenceRegion.objects.filter(assembly_id=assembly.assembly_id).all()[:1].get()
            assembly.example_chromosome = region.chromosome
            assembly.example_start = region.region_start
            assembly.example_end = region.region_stop
            print('\t', assembly.assembly_id, region.chromosome, region.region_start, region.region_stop)
            assembly.save()
        except SequenceRegion.DoesNotExist:
            print('No regions found {}'.format(assembly.ensembl_url))
        except SequenceRegion.MultipleObjectsReturned:
            print('Multiple assemblies found {}'.format(assembly.ensembl_url))


class Command(BaseCommand):
    """
    Usage:
    python manage.py update_ensembl_assembly
    """
    def handle(self, *args, **options):
        """Main function, called by django."""
        update_example_locations()
