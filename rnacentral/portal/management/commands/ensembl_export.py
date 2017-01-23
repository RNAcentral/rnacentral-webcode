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
import simplejson as json

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref


TRUSTED_DB = set([
    'GTRNADB',
    'MODOMICS',
    'LNCRNADB',
    'PDBE',
    'TAIR',
    'POMBASE',
    'DICTYBASE',
    'WORMBASE',
    'SGD',
])


class Exporter(object):
    def __init__(self, destination=None, test=False, **kwargs):
        self.destination = destination
        self.test = test
        self.filename = 'ensembl-xrefs.json'
        self.filepath = os.path.join(self.destination, self.filename)

    def get_high_quality_xrefs(self, rna):
        """
        Gets the high quality xrefs for the given sequence. A high quality
        xref is one that comes from a database in TRUSTED_DB and is not
        deleted.

        Parameters
        ----------
        rna : Rna
            The sequence to fetch the high quality xrefs for.

        Returns
        -------
        A query set of all high quality xrefs.
        """

        return Xref.objects.\
            filter(upi=rna.upi).\
            filter(deleted='N').\
            filter(db__descr__in=TRUSTED_DB)

    def find_xref_entries(self, taxid, xrefs):
        """
        Find all xrefs that come from the given taxon id, and format them as
        needed for export.

        Parameters
        ----------
        taxid : int
            The taxon id
        xrefs : iterable
            An iterable of Xref objects.

        Yields
        ------
        entry : dict
            A dictonary structured for export. This will contain an 'id' (the
            external id for the entry) and 'database' (the name of the
            database) keys.
        """

        data = []
        for xref in xrefs:
            if xref.taxid != taxid or not xref.accession.external_id:
                continue
            data.append({
                'id': xref.accession.external_id,
                'database': xref.db.display_name,
            })
        return data

    def format_xrefs(self, xrefs):
        """
        Find all xrefs that come from the given taxon id, and format them as
        needed for export.

        Parameters
        ----------
        taxid : int
            The taxon id
        xrefs : iterable
            An iterable of Xref objects.

        Yields
        ------
        entry : dict
            A dictonary structured for export. This will contain an 'id' (the
            external id for the entry) and 'database' (the name of the
            database) keys.
        """

        data = []
        for xref in xrefs:
            data.append({
                'id': xref.accession.external_id,
                'database': xref.db.display_name,
            })
        return data

    def get_data(self):
        """Get all data. If this Exporter is running as a test it will fetch
        the test data, otherwise it will fetch all Rna sequences. This will
        return an iterable of iterable, where each iterable consists of all
        xrefs that should be output for each sequence.
        """

        xrefs = Xref.objects.\
            filter(db__descr__in=TRUSTED_DB, deleted='N').\
            filter(accession__external_id__isnull=False).\
            select_related('upi', 'accession').\
            order_by('upi', 'taxid')

        if self.test:
            xrefs = xrefs[0:100]

        grouped = it.groupby(xrefs, lambda x: (x.upi, x.taxid))
        return it.imap(op.itemgetter(1), grouped)

    def structure_data(self, entries):
        """
        Structure the given data for export to ENSEMBL.

        Parameters
        ----------
        entries : iterable
            An iterable of Rna objects to export.

        Yields
        ------
        This will yield dictonaries suitable for export. Each dict will have
        """

        for xrefs in entries:
            xrefs = list(xrefs)
            rna = xrefs[0].upi
            taxid = xrefs[0].taxid
            yield {
                'rnacentral_id': '%s_%s' % (rna.upi, taxid),
                'description': rna.get_description(taxid=taxid),
                'sequence': rna.seq_short or rna.seq_long,
                'md5': rna.md5,
                'rna_type': rna.get_rna_type(taxid=taxid),
                'taxon_id': taxid,
                'xrefs': self.format_xrefs(xrefs),
            }

    def write(self, data, handle):
        """
        Actually write JSON formatted data. This is just a call to json.dump
        but setting the required flag so the iterable is treated as an array.
        """
        json.dump(data, handle, iterable_as_array=True)

    def __call__(self):
        """
        The main entry point for export. This will fetch the requested data and
        export it as JSON to the specified directory.
        """

        data = self.get_data()
        structured = self.structure_data(data)
        with open(self.filepath, 'wb') as out:
            self.write(structured, out)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination',
                    default='',
                    dest='destination',
                    help='[Required] Full path to the output directory'),

        make_option('-t', '--test',
                    action='store_true',
                    dest='test',
                    default=False,
                    help='[Optional] Run in test mode, which retrieves only a small subset of all data.'),
    )
    help = ('Export rnacentral data as json for import ensembl import')

    def handle(self, *args, **options):
        if not options['destination']:
            raise CommandError('Please specify --destination')
        Exporter(**options)()
