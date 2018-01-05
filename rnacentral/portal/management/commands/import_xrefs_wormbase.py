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

import re

from django.db import transaction
from django.core.management.base import BaseCommand
from portal.models import Xref, Database, Release, GenomicCoordinates, Reference_map, Accession


####################
# Export functions #
####################

@transaction.atomic
def run():
    """
    Source	Source primary accession	Source secondary accession	Target	Target primary accession	Target secondary accession
    WormBase	WBGene00000005	T13A10.10a	coding	CCD72062	FO081504
    WormBase	WBGene00000005	T13A10.10b	sequence	FO081504
    http://www.ebi.ac.uk/ena/data/xref/search?source=WormBase
    """
    filename = 'wormbase-xrefs.txt'
    found = not_found = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

        db = Database.objects.get(descr='WORMBASE')
        release = Release.objects.get(id=90)

        for i, line in enumerate(lines):
            if i == 0:
                continue # skip headers
            if 'sequence' not in line:
                continue # only look at non-coding lines
            fields = re.split('\t', line.rstrip())
            wormbase_accession = fields[1]
            locus_tag = fields[2]
            ena_accession = fields[4]

            xrefs = Xref.objects.filter(accession__locus_tag='CELE_' + locus_tag,
                                        accession__parent_ac=ena_accession,
                                        accession__database='ENA').all()
            if xrefs:
                continue

            if not xrefs:
                xrefs = Xref.objects.filter(accession__standard_name=locus_tag,
                                            accession__parent_ac=ena_accession,
                                            accession__database='ENA').all()
            else:
                not_found += 1
                # print line
                continue

            for xref in xrefs:
                found += 1
                accession = xref.accession
                ena_id = xref.accession.accession
                print('Found xref ' + ena_id)

                new_id = ':'.join([ena_id, 'WORMBASE', wormbase_accession])

                # update project id on the ENA xref
                accession.project = db.project_id
                accession.save()

                # create new xref object
                xref.pk = None
                xref.db = db
                xref.created = release
                xref.last = release
                xref.deleted = 'N'

                # create new accession object
                accession.accession = new_id
                accession.external_id = wormbase_accession
                accession.non_coding_id = ena_id
                accession.database = 'WORMBASE'
                accession.is_composite = 'Y'
                accession.project = db.project_id
                accession.save()

                coordinates = GenomicCoordinates.objects.filter(accession=ena_id).all()
                for coordinate in coordinates:
                    coordinate.accession = accession
                    print(coordinate)
                    coordinate.save()

                # create new reference_map object
                references = Reference_map.objects.filter(accession=ena_id).all()
                for reference in references:
                    reference.accession = accession
                    print(reference)
                    reference.save()

                # add accession object to xref and save
                xref.accession = accession
                xref.save()

            found += 1

        print('Found %i' % found)
        print('Not found %i' % not_found)


class Command(BaseCommand):
    """
    Usage:
    python manage.py import_xrefs
    """

    ########################
    # Command line options #
    ########################

    # shown with -h, --help
    help = ('Import cross-references from a text file.')

    def handle(self, *args, **options):
        """
        Django entry point.
        """
        run()
