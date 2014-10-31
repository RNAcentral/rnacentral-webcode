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
import re

####################
# Import functions #
####################

def mcl_import():
    """
    Example lines:
    URS000013BC07;  URS000075EDE5;  URS0000747EF9;
    """
    filename = '/Users/apetrov/Desktop/clustering/mcl/out.seq.mci.I90'
    f = open(filename, 'r')
    method_id = 5
    i = 0

    for line in f:
        upis = re.findall(r'URS[0-9A-F]{10}', line)
        cluster_id = 'mcl_i90_%i' % i
        i += 1
        cluster_size = len(upis)
        cluster = Clusters(cluster_id=cluster_id, method_id=method_id, size=cluster_size)
        cluster.save()

        for upi in upis:
            print upi
            cluster_member = ClusterMember(cluster_id=cluster_id,
                                           upi=upi,
                                           method_id=method_id)
            cluster_member.save()

    f.close()


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
        mcl_import()
