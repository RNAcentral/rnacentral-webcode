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

import csv
import json
import logging
from optparse import make_option

import attr
from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError

from portal.models import Rna

LOGGER = logging.getLogger(__name__)


@attr.s()  # pylint: disable=R0903
class Counts(object):
    """
    This just counts what we do with each sequence.
    """

    mapped = attr.ib(default=0)
    unmapped = attr.ib(default=0)
    total = attr.ib(default=0)
    none_possible = attr.ib(default=0)
    inconsitent = attr.ib(default=0)
    ensembl = attr.ib(default=0)
    ref_seq = attr.ib(default=0)


def read_rpi_lines(filename):
    """
    This will read the lines in MGI's RPI file into a saner format. That is it
    will put the header of the tsv file into a single line as is normal.
    """

    with open(filename, 'rb') as raw:
        header = "\t".join([next(raw).strip(), next(raw).strip()])
        yield header
        for line in raw:
            yield line


def parse_rpi(filename):
    """
    This will parse all the data in the RPI file into an iterable of dicts. The
    keys are lower cased and have '_' instead of ' '. The columns which contain
    ids will be split on '|' into a list.
    """

    for row in csv.DictReader(read_rpi_lines(filename), delimiter='\t'):
        entry = {}
        for key, value in row.items():
            cleaned_key = key.replace(' ', '_').lower()
            val = value
            if 'ids' in cleaned_key:
                if not value:
                    val = []
                else:
                    val = value.split('|')
            entry[cleaned_key] = val
        yield entry


class Mapper(object):
    """
    This will map as much MGI data as possible to known RNAcentral accessions.
    """

    def map_accessions(self, accessions):
        rna = Rna.objects.\
            filter(
                Q(xrefs__accession__parent_ac__in=accessions) |
                Q(xrefs__accession__external_id__in=accessions) |
                Q(xrefs__accession__optional_id__in=accessions)
            )

        return set(r.upi for r in rna)

    def rnacentral_id(self, counts, entry):

        ids = set()
        mgi_id = entry['accession']
        mappers = ['ensembl', 'ref_seq']
        for key in mappers:
            xrefs = entry['xref_data']
            accessions = xrefs[key]['transcript_ids']
            ids = self.map_accessions(accessions)
            if ids:
                setattr(counts, key, getattr(counts, key) + 1)
                break
        else:
            counts.none_possible += 1
            LOGGER.info("No possible mapping for %s", mgi_id)
            return None

        if not ids:
            LOGGER.info("Found no mappings for %s", mgi_id)
            return None

        if len(ids) > 1:
            counts.inconsitent += 1
            LOGGER.warn("Inconsistent rnacentral ids for %s", mgi_id)
            return None

        return ids.pop()

    def __call__(self, filename, savefile):
        data = []
        with open(filename, 'rb') as raw:
            data = json.load(raw)

        mapped = []
        counts = Counts()
        for entry in data:
            counts.total += 1
            rnacentral_id = self.rnacentral_id(counts, entry)
            if rnacentral_id is None:
                counts.unmapped += 1
                continue
            counts.mapped += 1
            result = {}
            result.update(entry)
            result['rnacentral_id'] = rnacentral_id
            mapped.append(result)

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
