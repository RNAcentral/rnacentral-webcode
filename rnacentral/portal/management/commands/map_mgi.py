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
from optparse import make_option

import attr
from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref

LOGGER = logging.getLogger(__name__)


@attr.s()  # pylint: disable=R0903
class Counts(object):
    """
    This just counts what we do with each sequence.
    """

    mapped = attr.ib(default=0)
    unmapped = attr.ib(default=0)
    total = attr.ib(default=0)
    all_failed = attr.ib(default=0)
    none_possible = attr.ib(default=0)
    inconsitent = attr.ib(default=0)
    ensembl = attr.ib(default=0)
    ref_seq = attr.ib(default=0)


class Mapper(object):
    """
    This will map as much MGI data as possible to known RNAcentral accessions.
    """

    def ensembl_upis(self, xref):
        rna = Xref.objects.filter(
            accession__external_id__in=xref['transcript_ids'],
            deleted='N'
        )
        return set(r.upi.upi for r in rna)

    def refseq_upis(self, xref):
        rna = Xref.objects.filter(
            accession__parent_ac__in=xref['transcript_ids'],
            deleted='N'
        )
        return set(r.upi.upi for r in rna)

    def rnacentral_id(self, counts, entry):

        print('Fetching id for %s' % entry)
        ids = set()
        mgi_id = entry['accession']
        mappers = [
            ('ensembl', self.ensembl_upis),
            ('ref_seq', self.refseq_upis),
        ]
        xrefs = entry['xref_data']
        for (key, method) in mappers:
            ids = method(xrefs[key])
            if ids:
                print(key)
                setattr(counts, key, getattr(counts, key) + 1)
                break
        else:
            if not sum(len(xrefs[k]['transcript_ids']) for k, m in mappers):
                counts.none_possible += 1
                print("No possible mapping for %s", mgi_id)
            else:
                counts.all_failed += 1
                print("Failed mapping for %s", mgi_id)
            return None

        result = sorted(ids)
        print('Found: %s -> %s', mgi_id, result)
        return result

    def __call__(self, filename, savefile):
        data = []
        with open(filename, 'rb') as raw:
            data = json.load(raw)

        mapped = []
        counts = Counts()
        for entry in data:
            counts.total += 1
            upis = self.rnacentral_id(counts, entry)
            if upis is None:
                counts.unmapped += 1
                continue
            counts.mapped += 1
            for upi in upis:
                result = {}
                result.update(entry)
                result['rnacentral_id'] = upi
                mapped.append(result)

        print(counts)
        with open(savefile, 'wb') as out:
            json.dumps(mapped, out)


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
