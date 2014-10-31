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

import collections
from django.core.management.base import BaseCommand
from portal.management.commands.common_exporters.oracle_connection \
    import OracleConnection


####################
# Import functions #
####################

class RnaTypesCounter(OracleConnection):
    """
    """

    def __init__(self):
        """
        """
        super(RnaTypesCounter, self).__init__()
        self.get_connection()
        self.get_cursor()
        sql = "select count(*) as cooccurence from rnc_rna_types t1, rnc_rna_types t2 where t1.upi = t2.upi and t1.rna_type = :rna_type1 and t2.rna_type= :rna_type2"
        self.cursor.prepare(sql)

    def count_rna_types(self):
        """
        """
        rna_types = [
        'rRNA',
        'misc_RNA',
        'tRNA',
        'piRNA',
        'other',
        'miRNA',
        'snRNA',
        'snoRNA',
        'siRNA',
        'hammerhead_ribozyme',
        'lncRNA',
        'SRP_RNA',
        'precursor_RNA',
        'antisense_RNA',
        'RNase_P_RNA',
        'tmRNA',
        'scRNA',
        'ribozyme',
        'RNase_MRP_RNA',
        'autocatalytically_spliced_intron',
        'vault_RNA',
        'rasiRNA',
        'telomerase_RNA',
        'guide_RNA',
        'Y_RNA',]

        for i in xrange(len(rna_types)):
            for j in xrange(i+1, len(rna_types)):
                yield (rna_types[i], rna_types[j])

    def run_query(self, rna_type1, rna_type2):
        """
        """
        self.cursor.execute(None, {'rna_type1': rna_type1, 'rna_type2': rna_type2})
        for row in self.cursor:
            result = self.row_to_dict(row)
            return result['cooccurence']

class Command(BaseCommand):
    """
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
        a = RnaTypesCounter()
        data = collections.defaultdict(dict)
        for rna_type1, rna_type2 in a.count_rna_types():
            count = a.run_query(rna_type1, rna_type2)
            print rna_type1, "-", rna_type2, ":", count
            data[rna_type1][rna_type2] = count
