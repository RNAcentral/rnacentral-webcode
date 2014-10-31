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
from portal.models import Rna, Clusters, ClusterMember

####################
# Import functions #
####################

def cluster_parse():
    """
    Example lines:
    chr1    17369   17436   URS000075A3E2
    chr1    29554   31109   URS000000192A,URS0000268115,URS000075CC93
    """
    filename = '/Users/apetrov/Desktop/clustering/bedtools_merge/separate_strands_d0.txt'
    f = open(filename, 'r')
    for line in f:
        (name, start, stop, ids) = line.rstrip().split('\t')
        members = ids.split(',')

        cluster_id = '_'.join([name, start, stop])
        cluster_size = len(members)
        method_id = 1

        name = name.replace('chr', '')

        print cluster_id, "\t", cluster_size
        cluster = Clusters(cluster_id=cluster_id,
                          method_id=method_id,
                          size=cluster_size,
                          start=start,
                          end=stop,
                          chromosome=name)
        cluster.save()

        for member in members:
            cluster_member = ClusterMember(cluster_id=cluster_id,
                                           upi=member,
                                           method_id=method_id)
            cluster_member.save()
            print member, "\t", cluster_id


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
        cluster_parse()
