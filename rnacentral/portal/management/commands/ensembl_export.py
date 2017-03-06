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

import os
import operator as op
import itertools as it
import subprocess as sp
import collections as coll

from optparse import make_option

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref

__doc__ = """
This will export all RNA sequences in the database and provide xref information
for a few selected databases. The database are not already part of Ensembl.
This will produce a simple JSON data structure for import into other databases.
"""


TRUSTED_DB = set([
    'gtrnadb',
    'lncrnadb',
    'mirbase',
    'modomics',
    'pdbe',
    'snopy'
    'srpdb',
    'tmrna website',
])
"""
This is the set of descr names for databases that we will provide xref entries
for.
"""

MOD_URL = 'http://modomics.genesilico.pl/sequences/list/{id}'


class SimpleXref(coll.namedtuple('SimpleXref',
                                 ['external_id', 'optional_id', 'database',
                                  'molecule_type'])):
    """
    Similar to SimpleSequence, this is just a basic container that is between
    the model and the serializer for this data. It contains some minimal logic
    for fields to write that are derived from the basic model.
    """

    def is_high_quality(self):
        name = self.database.lower()
        if name in TRUSTED_DB:
            return True
        if name == 'rfam':
            return self.molecule_type == 'seed'
        return False

    @classmethod
    def build(cls, xref):
        return cls(
            external_id=xref.accession.external_id,
            optional_id=xref.accession.optional_id,
            database=xref.db.display_name,
            molecule_type=xref.accession.mol_type,
        )

    @property
    def id(self):
        if self.database == 'PDBe':
            return '%s_%s' % (self.external_id, self.optional_id)
        if self.database == 'Modomics':
            return MOD_URL.format(id=self.external_id)
        return self.external_id


class SimpleSequence(coll.namedtuple('SimpleSequence',
                                     ['upi', 'taxon_id', 'description',
                                      'rna_type', 'seq_short', 'seq_long',
                                      'md5', 'xrefs'])):
    """
    This class represents a species specific entry in the RNA table. It
    serves to hold data that does not fit in the model (species specific
    description and rna type) as well as contain the tiny bit of logic for
    generating the needed fields for serializiation.
    """

    @classmethod
    def build(cls, xrefs):
        """
        Create a SimpleSequence given a list of xrefs for the sequence. This
        will create a SimpleSequence which may or may not have any xrefs. Only
        xrefs that come from the databases described in TRUSTED_DB will be used
        for the xrefs.
        """

        rna = xrefs[0].upi
        taxid = xrefs[0].taxid
        precomputed = rna.precomputed.get(taxid=taxid)
        simple = [SimpleXref.build(x) for x in xrefs]
        simple = [s for s in simple if s.is_high_quality()]

        return cls(
            upi=rna.upi,
            taxon_id=xrefs[0].taxid,
            description=precomputed.description,
            rna_type=precomputed.rna_type,
            seq_short=rna.seq_short,
            seq_long=rna.seq_long,
            md5=rna.md5,
            xrefs=simple,
        )

    @property
    def rnacentral_id(self):
        return '%s_%s' % (self.upi, self.taxon_id)

    @property
    def sequence(self):
        return self.seq_short or self.seq_long


class XrefSerializer(serializers.Serializer):
    id = serializers.CharField()
    database = serializers.CharField()


class RnaSerializer(serializers.Serializer):
    rnacentral_id = serializers.CharField()
    description = serializers.CharField()
    sequence = serializers.CharField()
    md5 = serializers.CharField()
    rna_type = serializers.CharField()
    taxon_id = serializers.IntegerField()
    xrefs = XrefSerializer(many=True)


class Exporter(object):
    def __init__(self, destination=None, test=False, min=None, max=None,
                 **kwargs):
        self.destination = destination
        self.min = min
        self.max = max
        if test:
            self.min = 0
            self.max = 10000
        self.filename = 'ensembl-xrefs.json'
        self.filepath = os.path.join(self.destination, self.filename)
        self.schema = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                   'export', 'schema', 'ensembl.json')

    def get_data(self, **kwargs):
        """
        Get all data. If this Exporter is running as a test it will fetch
        the test data, otherwise it will fetch all Rna sequences. This will
        return an iterable of iterable, where each iterable consists of all
        xrefs that should be output for each sequence.

        The given kwargs will be applied to the query and are generally useful
        for testing.
        """

        xrefs = Xref.objects.filter(deleted='N')

        if kwargs:
            xrefs = xrefs.filter(**kwargs)

        if self.min is not None:
            xrefs = xrefs.filter(upi__id__gte=self.min)

        if self.max is not None:
            xrefs = xrefs.filter(upi__id__lt=self.max)

        grouping = ('upi', 'taxid')
        xrefs = xrefs.\
            select_related('upi', 'accession', 'db').\
            prefetch_related('upi__precomputed').\
            order_by(*grouping)

        # This will group all xrefs by the tuple of values in their 'upi'
        # and 'taxid' attributes and then produce a iterable of iterables of
        # the grouped xrefs. This assumes the initial xrefs iterable is
        # ordered.
        fn = op.attrgetter(*grouping)  # A function to get the upi, taxid tuple
        grouped = it.groupby(xrefs, fn)  # Group by the tuple
        return it.imap(op.itemgetter(1), grouped)  # Create the iterables

    def structure_data(self, xrefs):
        """
        This will restructure the data from `get_data` from an iterable of
        iterables to an iterable of SimpleSequence objects.
        """
        return SimpleSequence.build(list(xrefs))

    def __call__(self):
        """
        The main entry point for export. This will fetch the requested data and
        export it as JSON to the specified directory.
        """

        structured = it.imap(self.structure_data, self.get_data())
        serializer = RnaSerializer(structured, many=True)
        with open(self.filepath, 'wb') as out:
            json = JSONRenderer().render(serializer.data)
            out.write(json)
        sp.check_call(['jsonschema', '-i', self.filepath, self.schema])


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
                    default='',
                    dest='destination',
                    help='[Required] Full path to the output directory'),

        make_option('--max',
                    dest='max',
                    type='int',
                    help='[Required] Maximum RNA id to output'),

        make_option('--min',
                    dest='min',
                    type='int',
                    help='[Required] Minimum RNA id to output'),


        make_option('-t', '--test',
                    action='store_true',
                    dest='test',
                    default=False,
                    help=('[Optional] Run in test mode, which retrieves only a'
                          ' small subset of all data.')),
    )
    help = ('Export rnacentral data as json for import ensembl import')

    def handle(self, *args, **options):
        if not options['destination']:
            raise CommandError('Please specify --destination')
        if options['test']:
            if options['min'] or options['max']:
                raise CommandError("Cannot specify test with --min or --max")
        else:
            if 'min' not in options:
                raise CommandError('Please specify --min')
            if 'max' not in options:
                raise CommandError('Please specify --max')
        Exporter(**options)()
