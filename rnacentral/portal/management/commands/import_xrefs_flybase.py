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
    AE013599	FBgn0266889	Dmel_CR45350
    AE014297	FBgn0267124	Dmel_CR45564
    """
    filename = 'flybase.tsv'
    found = not_found = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

        database = Database.objects.get(descr='FLYBASE')
        release = Release.objects.get(db_id=database.id)

        # print 'Deleting existing FlyBase Xrefs, Accessions, and Reference_maps'
        # Xref.objects.filter(db_id=database.id).delete()
        # Reference_map.objects.filter(accession__database=database.descr).delete()
        # Accession.objects.filter(database=database.descr).delete()

        for line in enumerate(lines):
            line = line.rstrip()
            fields = re.split('\t', line)
            parent_accession = fields[0]
            flybase_accession = fields[1]
            locus_tag = fields[2]

            xrefs = Xref.objects.filter(accession__parent_ac=parent_accession, accession__locus_tag=locus_tag, deleted='N').all()
            if len(xrefs) == 0:
                not_found += 1
                print line
                continue

            for xref in xrefs:
                # if one locus_tag matches several entries, find isoform id
                # in the note field, for example: Dana\GF27695-RC
                if len(xrefs) > 1:
                    regex = locus_tag.replace('_', '\\\\') + '-R[A-Z]+'
                    match = re.findall(regex, xref.accession.note)
                    if match:
                        locus_tag_versioned = match[0].replace('\\', '_')
                        print locus_tag_versioned
                    else:
                        print xref.accession.note
                        import pdb
                        pdb.set_trace()
                else:
                    locus_tag_versioned = None

                accession = xref.accession
                ena_id = xref.accession.accession
                print 'Found xref ' + ena_id

                if locus_tag_versioned:
                    new_id = locus_tag_versioned
                else:
                    new_id = locus_tag

                # update project id on the ENA xref
                accession.project = database.project_id
                accession.save()

                # create new xref object
                flybase_xref = xref
                flybase_xref.pk = None # make sure it does not overwrite the original xref
                flybase_xref.db = database
                flybase_xref.created = release
                flybase_xref.last = release

                # create new accession object
                flybase_ac = accession
                flybase_ac.accession = new_id
                flybase_ac.external_id = flybase_accession
                flybase_ac.non_coding_id = ena_id
                flybase_ac.database = 'FLYBASE'
                flybase_ac.is_composite = 'Y'
                flybase_ac.project = database.project_id
                flybase_ac.save()

                # add accession object to xref and save
                flybase_xref.accession = flybase_ac
                flybase_xref.save()

                coordinates = GenomicCoordinates.objects.filter(accession=ena_id).all()
                for coordinate in coordinates:
                    coordinate.accession = flybase_ac
                    coordinate.save()

                # create new reference_map object
                references = Reference_map.objects.filter(accession=ena_id).all()
                for reference in references:
                    reference.accession = flybase_ac
                    reference.save()

            found += 1

        print 'Found %i' % found
        print 'Not found %i' % not_found


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
