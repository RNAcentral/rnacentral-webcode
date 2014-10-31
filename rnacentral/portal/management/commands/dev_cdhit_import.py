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

def cd_hit_import():
    """
    Example lines:
    >Cluster 0
    0   205012nt, >URS000019E0CD;... *
    >Cluster 1
    0   91667nt, >URS00000CE0D1;... at +/100.00%
    1   91671nt, >URS0000759CF4;... *
    """
    filename = '/Users/apetrov/Desktop/clustering/cd-hit/run3/human_output.txt.clstr'
    lines = open(filename).readlines()
    i = 0

    method_id = 2
    r = re.compile('URS[0-9A-F]{10}')

    while i < len(lines):
        cluster_line = lines[i].rstrip()
        c = i + 1
        members = []
        while c < len(lines) and lines[c][0] != '>':
            member_line = lines[c].rstrip()
            c += 1
            members.append(r.search(member_line).group())
        i = c

        cluster_id = cluster_line.replace('>','').replace(' ','_').lower()
        print cluster_id
        cluster_size = len(members)
        cluster = Clusters(cluster_id=cluster_id, method_id=method_id, size=cluster_size)
        cluster.save()

        for member in members:
            print member
            cluster_member = ClusterMember(cluster_id=cluster_id,
                                           upi=member,
                                           method_id=method_id)
            cluster_member.save()


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
        cd_hit_import()
