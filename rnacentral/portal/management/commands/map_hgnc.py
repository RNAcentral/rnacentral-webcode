"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

from __future__ import print_function

import json
import hashlib
import re
import requests
import collections as coll
import operator as op

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from portal.models import Xref, Rna
from django.db import connection

"""
Map HGNC ncRNAs to RNAcentral identifiers.

HGNC JSON file is available at:
ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/json/locus_groups/non-coding_RNA.json

Usage:
python manage.py map_hgnc -i /path/to/hgnc/json/file

To run in test mode:
python manage.py map_hgnc -i /path/to/hgnc/json/file -t
"""

ENSEMBL_QUERY = """
select
    xref.upi,
    acc.optional_id,
    rna.len
from xref
join rnc_accessions acc on acc.accession = xref.ac
join rna on rna.upi = xref.upi
where
    xref.dbid = 25
    and xref.taxid = 9606
    and xref.deleted = 'N'
;
"""


def get_ensembl_mapping():
    with connection.cursor() as cursor:
        complete_mapping = coll.defaultdict(set)
        cursor.execute(ENSEMBL_QUERY)
        for row in cursor.fetchall():
            gene, _ = row[1].split('.')
            complete_mapping[gene].add((row[0], int(row[2])))

    mapping = {}
    for gene, ids in complete_mapping.items():
        if not len(ids):
            continue
        best, _ = max(ids, key=op.itemgetter(1))
        mapping[gene] = best
    return mapping


class HGNCMapper():
    """
    Class for mapping HGNC ncRNAs to RNAcentral identifiers.
    """
    def __init__(self, **kwargs):
        """
        Store command line options.
        """
        self.test = kwargs['test']
        self.hgnc_json_file = kwargs['hgnc_json_file']
        self.data = None
        self.hgnc_with_rnacentral_ids = []

    def get_hgnc_data(self):
        """
        Read in HGNC data in JSON format.
        """
        with open(self.hgnc_json_file, 'r') as f:
            self.data = json.load(f)['response']['docs']

    def find_rnacentral_matches(self):
        """
        Map HGNC ncRNAs to RNAcentral using RefSeq, Vega, gtRNAdb accessions
        and sequence matches.
        """
        found = 0
        no_match = 0
        ensembl_mapping = get_ensembl_mapping()
        match_refseq = match_gtrnadb = match_sequence = match_ensembl = 0
        for i, entry in enumerate(self.data):
            if self.test and i > 20:
                break
            rnacentral_id = None

            if 'refseq_accession' in entry and not rnacentral_id:
                rnacentral_id = self.get_rnacentral_id(entry['refseq_accession'][0])
                if rnacentral_id:
                    match_refseq += 1

            if entry['locus_type'] == 'RNA, transfer' and not rnacentral_id:
                gtrnadb_id = self.get_gtrnadb_id(entry['symbol'])
                if gtrnadb_id:
                    rnacentral_id = self.get_rnacentral_for_gtrnadb(gtrnadb_id)
                    if rnacentral_id:
                        match_gtrnadb += 1

            if not rnacentral_id:
                if 'ensembl_gene_id' in entry:
                    gene_id = entry['ensembl_gene_id']
                    fasta = self.get_sequence_fasta(gene_id)
                    if not fasta:
                        continue
                    md5 = self.get_md5(fasta)
                    rnacentral_id = self.get_rnacentral_id_by_md5(md5)
                    if rnacentral_id:
                        match_sequence += 1
                    else:
                        rnacentral_id = ensembl_mapping.get(gene_id, None)
                        if rnacentral_id:
                            match_ensembl += 1

            if rnacentral_id:
                print('%s\t%s\t%s' % (rnacentral_id, entry['symbol'], entry['name']))
                entry['rnacentral_id'] = rnacentral_id
                found += 1
            else:
                print('No match\t%s\t%s\t%s' % (entry['name'], entry['symbol'], entry['symbol']))
                entry['rnacentral_id'] = None
                no_match += 1
            self.hgnc_with_rnacentral_ids.append(entry)

        print('%i matches found' % found)
        print('%i RefSeq matches' % match_refseq)
        print('%i GtRNAdb matches' % match_gtrnadb)
        print('%i sequence matches' % match_sequence)
        print('%i no match' % no_match)

    def get_sequence_fasta(self, ensembl_id):
        """
        Get sequence based on Ensembl Gene id.
        """
        url = 'https://rest.ensembl.org/sequence/id/' + ensembl_id + '?content-type=text/plain'
        response = requests.get(url)
        try:
            response.raise_for_status()
        except:
            return None
        return response.text

    def get_md5(self, sequence):
        """
        Calculate md5 for an RNA sequence
        """
        sequence = sequence.replace('U','T').upper()
        m = hashlib.md5()
        m.update(sequence)
        return m.hexdigest()

    def get_rnacentral_id_by_md5(self, md5):
        """
        Get RNAcentral identifier matching an MD5 checksum.
        """
        try:
            rna = Rna.objects.filter(md5=md5).get()
        except Rna.DoesNotExist:
            rna = None
        if rna:
            return rna.upi
        else:
            return None

    def get_gtrnadb_id(self, accession):
        """
        Convert HGNC symbols into GtRNAdb identifiers.
        """
        one_to_three = {
            'A': 'Ala',
            'C': 'Cys',
            'D': 'Asp',
            'E': 'Glu',
            'F': 'Phe',
            'G': 'Gly',
            'H': 'His',
            'I': 'Ile',
            'K': 'Lys',
            'L': 'Leu',
            'M': 'Met',
            'N': 'Asn',
            'P': 'Pro',
            'Q': 'Gln',
            'R': 'Arg',
            'S': 'Ser',
            'T': 'Thr',
            'U': 'SeC',
            'V': 'Val',
            'W': 'Trp',
            'Y': 'Tyr',
            'X': 'iMet',
            'SUP': 'Sup',
        }
        m = re.match(r'TR(\S+)-(\S{3})(\d+-\d+)', accession)
        if m:
            return "tRNA-" + one_to_three[m.group(1)] + "-" + m.group(2) + "-" + m.group(3)
        # nuclear-encoded mitochondrial tRNAs
        m = re.match(r'NMTR(\S+)-(\S{3})(\d+-\d+)', accession)
        if m:
            return "nmt-tRNA-" + one_to_three[m.group(1)] + "-" + m.group(2) + "-" + m.group(3)
        return None

    def get_rnacentral_for_gtrnadb(self, accession):
        rna = Rna.objects.filter(
            xrefs__accession__optional_id=accession,
            xrefs__accession__database="GTRNADB",
            xrefs__taxid=9606,
            xrefs__deleted='N',
            xrefs__db__id=8,
        ).order_by('-length')

        rna = rna.first()
        if rna:
            return rna.upi
        else:
            return None

    def get_rnacentral_id(self, accession):
        """
        Get RNAcentral id based on external accession.
        When multiple alternative sequences match an identifier
        (in case of Vega IDs, for example),
        get the longest.
        """
        rna = Rna.objects.filter(
            Q(xrefs__accession__parent_ac=accession, xrefs__taxid=9606, xrefs__deleted='N') |
            Q(xrefs__accession__external_id=accession, xrefs__taxid=9606, xrefs__deleted='N') |
            Q(xrefs__accession__optional_id=accession, xrefs__taxid=9606, xrefs__deleted='N')
        ).order_by('-length')

        rna = rna.first()
        if rna:
            return rna.upi
        else:
            return None

    def export_hgnc_rnacentral_mapping(self):
        """
        Export HGNC data in JSON format with a new RNAcentral_id field.
        """
        filename = 'hgnc_rnacentral.json'
        with open(filename, 'w') as outfile:
            json.dump(self.hgnc_with_rnacentral_ids, outfile)

    def __call__(self):
        """
        Main import function.
        """
        print('Mapping HGNC ncRNAs to RNAcentral identifiers')
        self.get_hgnc_data()
        self.find_rnacentral_matches()
        self.export_hgnc_rnacentral_mapping()
        print('%i entries' % len(self.data))
        print('Done')


class Command(BaseCommand):
    """
    Handle command line options.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-i', '--input',
            dest='hgnc_json_file',
            default=False,
            help='[Required] Path to HGNC JSON file')
        parser.add_argument(
            '-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode to process only the first few entries')

    # shown with -h, --help
    help = ('Map HGNC accessions to RNAcentral identifiers. Requires a JSON file from HGNC.')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['hgnc_json_file']:
            raise CommandError('Please specify HGNC input file')
        HGNCMapper(**options)()
