# -*- coding: utf-8 -*-

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

import json
from datetime import datetime

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref
from portal.models import Database
from portal.models import Accession
from portal.models import Reference_map
from portal.models import Release


class MgiImporter(object):
    def __init__(self):
        self.database = Database.objects.get(descr='MGI')
        self.release = Release.objects.get(db_id=self.database.id)
        self.reference = self.database.references()[0]

    def delete_current_data(self):
        Xref.objects.filter(db_id=self.database.id).delete()
        Reference_map.objects.filter(accession__database=self.database.descr).delete()
        Accession.objects.filter(database=self.database.descr).delete()

    def xref(self, entry):
        return Xref(
            db_id=self.database.id,
            accession_id=entry['accession'],
            created_id=self.release.id,
            last_id=self.release.id,
            upi_id=entry['rnacentral_id'],
            version_i=1,
            deleted='N',
            timestamp=datetime.now(),
            userstamp='RNACEN',
            version=1,
            taxid=entry['ncbi_taxon_id'],
        )

    def accession(self, entry):
        return Accession(
            accession=entry['accession'],
            description=entry['name'],
            division=entry['division'],
            species=entry['species'],
            is_composite='N',
            database=entry['database'],
            classification=entry['lineage'],
            external_id=entry['accession'],
            feature_name=entry['feature_name'],
            ncrna_class=entry['ncrna_class'],
            gene=entry['gene'],
            note=json.dumps(entry['note']),
            xref=json.dumps(entry['xref_data']),
        )

    def references(self, entry):
        return Reference_map(
            accession_id=entry['acccession'],
            data_id=self.reference.id
        )

    def __call__(self, filename):
        with open(filename, 'rb') as raw:
            data = json.load(raw)

        self.delete_current_data()
        for entry in data:
            self.xref(entry).create_or_update()
            self.accession(entry).create_or_update()
            self.references(entry).create_or_update()


class Command(BaseCommand):
    """
    Handle command line options.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '-i',
            '--input',
            dest='json_file',
            default=False,
            help='[Required] Path to MGI JSON file with RNAcentral identifiers'),
    )
    # shown with -h, --help
    help = ('Import HGNC cross-references into RNAcentral database')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['json_file']:
            raise CommandError('Please specify MGI input file')
        MgiImporter()(options['json_file'])
