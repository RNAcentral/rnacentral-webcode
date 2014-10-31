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
from portal.models import Xref
import pdb

####################
# Import functions #
####################

def export():
    """
    """
    species = 9606 # homo sapiens

    def export_mirbase():
        """
        """
        clusters = []
        filename = 'mirbase.txt'

        # get all mirbase accessions
        xrefs = Xref.objects.filter(db__display_name='miRBase',
                                    deleted='N',
                                    taxid=species,
                                    accession__feature_name='precursor_RNA').\
                             iterator ()

        for xref in xrefs:
            precursor = xref.upi.upi
            matures = xref.get_mirbase_mature_products()
            if matures:
                clusters.append([precursor] + [x.upi for x in matures])
            else:
                print 'Mature miRNAs not found'

        upis = 0

        f = open(filename, 'w')
        for cluster in clusters:
            f.write('\t'.join(cluster))
            f.write("\n")
            upis += len(cluster)
        f.close()

        print "Total sequences: %i" % upis
        print "Clusters: %i" % len(clusters)


    def export_vega():
        """
        """
        clusters = []
        filename = 'vega.txt'

        xrefs = Xref.objects.filter(deleted='N',
                                    taxid=species,
                                    db__descr='VEGA').\
                             select_related('accession').\
                             order_by('accession__external_id').\
                             iterator()
        prev_gene_id = ''
        for xref in xrefs:
            gene_id = xref.accession.external_id
            if gene_id != prev_gene_id:
                clusters.append([xref.upi.upi])
                prev_gene_id = gene_id
            else:
                clusters[-1].append(xref.upi.upi)

        upis = 0

        f = open(filename, 'w')
        for cluster in clusters:
            f.write('\t'.join(cluster))
            f.write("\n")
            upis += len(cluster)
        f.close()

        print "Total sequences: %i" % upis
        print "Clusters: %i" % len(clusters)


    def export_refseq():
        """
        """
        clusters = []
        filename = 'refseq.txt'

        xrefs = Xref.objects.filter(deleted='N',
                                    taxid=species,
                                    db__descr='REFSEQ').\
                             select_related('accession').\
                             order_by('accession__db_xref').\
                             iterator()
        prev_gene_id = ''
        for xref in xrefs:
            gene_id = xref.get_ncbi_gene_id()
            if gene_id != prev_gene_id:
                clusters.append([xref.upi.upi])
                prev_gene_id = gene_id
            else:
                clusters[-1].append(xref.upi.upi)

        upis = 0

        f = open(filename, 'w')
        for cluster in clusters:
            f.write('\t'.join(cluster))
            f.write("\n")
            upis += len(cluster)
        f.close()

        print "Total sequences: %i" % upis
        print "Clusters: %i" % len(clusters)


    # export_mirbase()
    # export_vega()
    export_refseq()


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
        export()
