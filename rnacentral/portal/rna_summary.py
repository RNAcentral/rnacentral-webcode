"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This module contains code to detect certain types of problems with Rfam matches
to sequences. That is it can find if the sequence and Rfam domain conflict, or
if the sequence is only a partial sequence
"""

import re

import requests


class RnaSummary(object):
    """
    This objects retrieves the information required for generating an automated
    summary for an RNA sequence. It uses the EBI search for data retrieval
    in order to avoid overloading the database.
    """
    def __init__(self, urs, taxid, endpoint='http://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral'):
        self.urs = urs
        self.taxid = taxid
        self.endpoint = endpoint
        self.count_distinct_organisms = self.get_species_count(urs)
        if not self.taxid:
            return
        raw_data = self.get_raw_data(urs, taxid)
        if len(raw_data['entries']) == 0:
            self.entry_found = False
            return
        entry = raw_data['entries'][0]['fields']
        self.entry_found = True
        self.citations_count = entry['n_citations'][0]
        self.common_name = entry['common_name'][0] if entry['common_name'] else ''
        self.databases = entry['expert_db']
        self.database_count = len(self.databases)
        self.description = entry['description'][0] if len(entry['description']) > 0 else ''
        self.genes = entry['gene']
        self.has_genomic_coordinates = entry['has_genomic_coordinates'][0]
        self.has_go_annotations = entry['has_go_annotations'][0]
        self.has_interacting_proteins = entry['has_interacting_proteins'][0]
        self.has_interacting_rnas = entry['has_interacting_rnas'][0] if len(entry['has_interacting_rnas']) > 0 else None
        self.has_secondary_structure = entry['has_secondary_structure'][0]
        self.interacting_proteins = entry['interacting_protein']
        self.interacting_rnas = entry['interacting_rna']
        self.length = entry['length'][0]
        self.product = entry['interacting_protein']
        self.rfam_family_name = entry['rfam_family_name']
        self.rfam_id = entry['rfam_id']
        self.rfam_count = len(self.rfam_id)
        self.rna_type = entry['rna_type'][0]
        self.species = entry['species'][0] if len(entry['species']) > 0 else ''
        self.pretty_so_rna_type_name = self.parse_so_rna_type_name(entry['so_rna_type_name'][0]) if len(entry['so_rna_type_name']) > 0 else ''
        self.so_rna_type_name = self.convert_string_to_array(entry['so_rna_type_name'][0]) if len(entry['so_rna_type_name']) > 0 else ''


    def get_raw_data(self, urs, taxid):
        fields = [
            'common_name',
            'description',
            'expert_db',
            'gene',
            'has_genomic_coordinates',
            'has_go_annotations',
            'has_interacting_proteins',
            'has_interacting_rnas',
            'has_secondary_structure',
            'interacting_protein',
            'interacting_rna',
            'length',
            'n_citations',
            'product',
            'rfam_family_name',
            'rfam_id',
            'rna_type',
            'species',
            'so_rna_type_name',
        ]
        url = '{endpoint}/entry/{urs}_{taxid}?format=json&fields={fields}'.format(
            urs=urs,
            taxid=taxid,
            fields=','.join(fields),
            endpoint=self.endpoint
        )
        data = requests.get(url)
        return data.json()

    def get_species_count(self, urs):
        url = '{endpoint}?query={urs}* NOT TAXONOMY:"{taxid}"&format=json'.format(
            urs=urs,
            endpoint=self.endpoint,
            taxid=self.taxid
        )
        try:
            data = requests.get(url)
            return max(int(data.json()['hitCount']), 1)
        except:
            return 1

    def convert_string_to_array(self, target):
        so_terms = re.sub(r'[\[\]\'\s]', '', target)
        if not so_terms:
            return None
        so_terms = so_terms.split(',')
        if len(so_terms) > 1:
            so_terms.remove('ncRNA')
        return so_terms

    def pretty_so_terms(self, so_term):
        exceptions = ['RNase_P_RNA', 'SRP_RNA', 'Y_RNA', 'RNase_MRP_RNA']
        if so_term not in exceptions:
            so_term = so_term[0].lower() + so_term[1:]
        if so_term == 'lnc_RNA':
            so_term = 'lncRNA'
        elif so_term == 'pre_miRNA':
            so_term = 'pre-miRNA'
        else:
            so_term = so_term.replace('_', ' ')
        return so_term

    def parse_so_rna_type_name(self, so_rna_type_name):
        """
        Turn "['ncRNA', 'lnc_RNA']" into an array of strings.
        """
        so_terms = self.convert_string_to_array(so_rna_type_name)
        if not so_terms:
            return ''
        pretty_so_terms = []
        for so_term in so_terms:
            pretty_so_terms.append(self.pretty_so_terms(so_term))
        return pretty_so_terms
