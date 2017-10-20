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
from portal.models import Accession
from portal.models import Database
from portal.models import Release
from portal.models.reference_map import Reference_map
from portal.models import Reference


class MgiImporter(object):
    def __init__(self):
        self.database_name = 'MGI'
        self.database = Database.objects.get(descr=self.database_name)
        self.release = Release.objects.get(db_id=self.database.id)
        self.reference_id = Reference.objects.filter(
            md5='fd169d8e25abb306cbdc773b09a819f8',
            doi='10.1093/nar/gkw1040',
        ).first().id

    def delete_current_data(self):
        Xref.objects.filter(db_id=self.database.id).delete()
        Accession.objects.filter(database=self.database_name).delete()
        Reference_map.objects.filter(accession__database=self.database_name).delete()

    def save_xref(self, entry):
        Xref.update_or_create(
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
            taxid=entry['ncbi_taxon_id'],
        )

    def save_accession(self, entry):
        Accession.create_or_update(
            accession=entry['accession'],
            parent_ac=entry['parent_accession'],
            seq_version=entry['seq_version'],
            feature_start=entry['feature_location_start'],
            feature_end=entry['feature_location_end'],
            feature_name=entry['feature_name'],
            ordinal=entry['ordinal'],
            division=entry['division'],
            description=entry['description'],
            species=entry['species'],
            organelle=entry['organelle'],
            classification=entry['classification'],
            project=entry['project'],
            is_composite=entry['is_composite'],
            non_coding_id=entry['non_coding_id'],
            database=entry['database'],
            external_id=entry['external_id'],
            optional_id=entry['optional_id'],
            common_name=entry['common_name'],
            allele=entry['allele'],
            anticodon=entry['anticodon'],
            chromosome=entry['chromosome'],
            experiment=entry['experiment'],
            function=entry['function'],
            gene=entry['gene'],
            gene_synonym=entry['gene_synonym'],
            inference=entry['inference'],
            locus_tag=entry['locus_tag'],
            map=entry['map'],
            mol_type=entry['mol_type'],
            ncrna_class=entry['ncrna_class'],
            note=json.dumps(entry['note_data']),
            old_locus_tag=entry['old_locus_tag'],
            operon=entry['operon'],
            product=entry['product'],
            psuedogene=entry['psuedogene'],
            standard_name=entry['standard_name'],
            db_xref=json.dumps(entry['xref_data']),
        )

    def save_references(self, entry):
        Reference_map.update_or_create(
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

            self.save_xref(entry)
            self.save_accession(entry)
            self.save_references(entry)


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
