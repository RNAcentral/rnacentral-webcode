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

from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref
from portal.models import Accession
from portal.models import Database
from portal.models import Release
from portal.models.reference_map import Reference_map
from portal.models import Reference


class MgiImporter(object):
    def __init__(self):
        self.database_name = 'MGI'
        self.database = Database.objects.get(descr=self.database_name)
        self.reference_id = Reference.objects.get(doi='10.1093/nar/gkw1040').id
        self.release = self.create_release()

    def create_release(self):
        now = datetime.now()
        release = Release()
        release.id = self.next_release_id()
        release.db = self.database
        release.release_date = now
        release.release_type = 'F'
        release.status = 'L'
        release.timestamp = now
        release.userstamp = 'RNACEN'
        release.force_load = 'N'
        release.save()
        return release

    def next_release_id(self):
        return Release.objects.all().aggregate(Max('id'))['id__max'] + 1

    def delete_current_data(self):
        Xref.default_objects.filter(db_id=self.database.id).delete()
        Accession.objects.filter(database=self.database_name).delete()
        Reference_map.objects.filter(accession__database=self.database_name).delete()

    def save_xref(self, entry):
        Xref.default_objects.update_or_create(
            db_id=self.database.id,
            created_id=self.release.id,
            last_id=self.release.id,
            upi_id=entry['rnacentral_id'],
            version_i=1,
            deleted='N',
            timestamp=datetime.now(),
            userstamp='RNACEN',
            accession_id=entry['accession'],
            version=1,
            taxid=entry['ncbi_tax_id'],
        )

    def save_accession(self, entry):
        xref_data = json.dumps(entry['xref_data'])
        if len(xref_data) > 800:
            xref_data = ''
        Accession.objects.update_or_create(
            accession=entry['accession'],
            parent_ac=entry['parent_accession'],
            seq_version=entry['seq_version'],
            feature_start=entry['feature_location_start'],
            feature_end=entry['feature_location_end'],
            feature_name=entry['feature_type'],
            ordinal=entry['ordinal'],
            division=entry['division'],
            description=entry['description'],
            species=entry['species'],
            organelle=entry['organelle'],
            classification=entry['lineage'],
            project=entry['project'],
            is_composite=entry['is_composite'],
            non_coding_id=entry['non_coding_id'],
            database=entry['database'],
            external_id=entry['external_id'],
            optional_id=entry['optional_id'],
            # common_name=entry['common_name'],
            # allele=entry['allele'],
            anticodon=entry['anticodon'],
            # chromosome=entry['chromosome'],
            experiment=entry['experiment'],
            function=entry['function'],
            gene=entry['gene'],
            gene_synonym='; '.join(entry['gene_synonyms']),
            inference=entry['inference'],
            locus_tag=entry['locus_tag'],
            # map=entry['map'],
            mol_type=entry['mol_type'],
            ncrna_class=entry['ncrna_class'],
            note=json.dumps(entry['note_data']),
            old_locus_tag=entry['old_locus_tag'],
            product=entry['product'],
            # pseudogene=entry['pseudogene'],
            standard_name=entry['standard_name'],
            db_xref=xref_data,
        )

    def save_references(self, entry):
        Reference_map.objects.update_or_create(
            accession_id=entry['accession'],
            data_id=self.reference_id,
        )

    def __call__(self, filename):
        with open(filename, 'rb') as raw:
            data = json.load(raw)

        self.delete_current_data()
        for entry in data:
            if not entry['rnacentral_id']:
                continue

            print('Saving %s' % entry['accession'])
            self.save_accession(entry)
            self.save_references(entry)
            self.save_xref(entry)
            print('Saved')

        self.release.status = 'D'
        self.release.save()


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
    help = ('Import all MGI data into RNAcentral database')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['json_file']:
            raise CommandError('Please specify MGI input file')
        MgiImporter()(options['json_file'])
