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
import logging
from collections import Counter
from optparse import make_option

from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError

from portal.models import Rna

LOGGER = logging.getLogger(__name__)


class Mapper(object):
    def ensembl_accession(self, ensembl_id):
        return ensembl_id

    def refseq_accession(self, refseq_id):
        return refseq_id

    def map_accessions(self, accessions):
        rna = Rna.objects.\
            filter(
                Q(xrefs__accession__parent_ac__in=accessions) |
                Q(xrefs__accession__external_id__in=accessions) |
                Q(xrefs__accession__optional_id__in=accessions)
            )

        return set(r.upi for r in rna)

    def rnacentral_id(self, counts, entry):
        mappers = [
            ('ensembl_transcript_ids', self.ensembl_accession),
            ('refseq_transcript_ids', self.refseq_accession),
        ]

        seen = False
        ids = set()
        for (key, method) in mappers:
            if not ids:
                counts[key] += 1
                accessions = [method(mid) for mid in entry[key]]
                ids = self.map_accessions(accessions)
                seen = True

        mgi_id = entry['mgi_marker']
        if not seen:
            LOGGER.info("No possible mapping for %s", mgi_id)
            return None

        if not ids:
            LOGGER.info("Found no mappings for %s", mgi_id)
            return None

        if len(ids) > 1:
            LOGGER.warn("Inconsistent rnacentral ids for %s", mgi_id)
            return None

        return ids.pop()

    def map_data(self, data):
        counts = Counter()
        mapped = []
        for entry in data:
            result = {}
            result.update(entry)
            rnacentral_id = self.rnacentral_id(counts, entry)
            if rnacentral_id is None:
                continue
            result['rnacentral_id'] = rnacentral_id
            mapped.append(result)
        return mapped

    def __call__(self, filename, savefile):
        with open(filename, 'rb') as raw:
            data = json.loads(raw)

        mapped = self.map_data(data)

        with open(savefile, 'wb') as out:
            json.dumps(out, mapped)


class Command(BaseCommand):
    """
    Handle command line options.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '-i',
            '--input',
            dest='input',
            default=False,
            help='[Required] Path to input JSON file'
        ),
        make_option(
            '-o',
            '--output',
            dest='output',
            default=False,
            help='[Required] Path to file to save to',
        )
    )
    # shown with -h, --help
    help = ('Map HGNC accessions to RNAcentral identifiers. Requires a JSON file from MGI.')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['input']:
            raise CommandError('Please specify HGNC input file')
        Mapper()(options['input'], options['output'])
