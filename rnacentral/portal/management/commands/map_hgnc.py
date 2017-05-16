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

import json
import hashlib
import re
import requests

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from portal.models import Xref, Accession, Rna

"""
Map HGNC ncRNAs to RNAcentral identifiers.

HGNC JSON file is available at:
ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/json/locus_groups/non-coding_RNA.json

Usage:
python manage.py map_hgnc -i /path/to/hgnc/json/file

To run in test mode:
python manage.py map_hgnc -i /path/to/hgnc/json/file -t
"""

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
        match_refseq = match_vega = match_gtrnadb = match_sequence = 0
        for i, entry in enumerate(self.data):
            if self.test and i > 20:
                break
            rnacentral_id = None
            if 'refseq_accession' in entry and not rnacentral_id:
                rnacentral_id = self.get_rnacentral_id(entry['refseq_accession'][0])
                if rnacentral_id:
                    match_refseq += 1
            if 'vega_id' in entry and not rnacentral_id:
                rnacentral_id = self.get_rnacentral_id(entry['vega_id'])
                if rnacentral_id:
                    match_vega += 1
            if entry['locus_type'] == 'RNA, transfer' and not rnacentral_id:
                gtrnadb_id = self.get_gtrnadb_id(entry['symbol'])
                if gtrnadb_id:
                    rnacentral_id = self.get_rnacentral_id(gtrnadb_id)
                    if rnacentral_id:
                        match_gtrnadb += 1
            if not rnacentral_id:
                if 'ensembl_gene_id' in entry:
                    fasta = self.get_sequence_fasta(entry['ensembl_gene_id'])
                    md5 = self.get_md5(fasta)
                    rnacentral_id = self.get_rnacentral_id_by_md5(md5)
                    if rnacentral_id:
                        match_sequence += 1
            if rnacentral_id:
                print '%s\t%s\t%s' % (rnacentral_id, entry['symbol'], entry['name'])
                entry['rnacentral_id'] = rnacentral_id
                found += 1
            else:
                print 'No match\t%s\t%s\t%s' % (entry['name'], entry['symbol'], entry['symbol'])
                entry['rnacentral_id'] = None
                no_match += 1
            self.hgnc_with_rnacentral_ids.append(entry)

        print '%i matches found' % found
        print '%i RefSeq matches' % match_refseq
        print '%i Vega matches' % match_vega
        print '%i GtRNAdb matches' % match_gtrnadb
        print '%i sequence matches' % match_sequence
        print '%i no match' % no_match

    def get_sequence_fasta(self, ensembl_id):
        """
        Get sequence based on Ensembl Gene id.
        """
        url='https://rest.ensembl.org/sequence/id/' + ensembl_id + '?content-type=text/plain'
        return requests.get(url).text

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

    def get_rnacentral_id(self, accession):
        """
        Get RNAcentral id based on external accession.
        When multiple alternative sequences match an identifier
        (in case of Vega IDs, for example),
        get the longest.
        """
        rna = Rna.objects.filter(
                    Q(xrefs__accession__parent_ac=accession) |
                    Q(xrefs__accession__external_id=accession) |
                    Q(xrefs__accession__optional_id=accession)). \
                filter(xrefs__taxid=9606, xrefs__deleted='N').\
                order_by('-length').\
                first()
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
        print 'Mapping HGNC ncRNAs to RNAcentral identifiers'
        self.get_hgnc_data()
        self.find_rnacentral_matches()
        self.export_hgnc_rnacentral_mapping()
        print '%i entries' % len(self.data)
        print 'Done'


class Command(BaseCommand):
    """
    Handle command line options.
    """
    option_list = BaseCommand.option_list + (
        make_option('-i', '--input',
            dest='hgnc_json_file',
            default=False,
            help='[Required] Path to HGNC JSON file'),
        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode to process only the first few entries'),
    )
    # shown with -h, --help
    help = ('Map HGNC accessions to RNAcentral identifiers. Requires a JSON file from HGNC.')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['hgnc_json_file']:
            raise CommandError('Please specify HGNC input file')
        HGNCMapper(**options)()
