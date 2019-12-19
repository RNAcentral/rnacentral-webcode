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
        self.entry_found = True
        self.citations_count = raw_data['entries'][0]['fields']['n_citations'][0]
        self.common_name = raw_data['entries'][0]['fields']['common_name'][0] if raw_data['entries'][0]['fields']['common_name'] else ''
        self.databases = raw_data['entries'][0]['fields']['expert_db']
        self.database_count = len(self.databases)
        self.description = raw_data['entries'][0]['fields']['description'][0]
        self.genes = raw_data['entries'][0]['fields']['gene']
        self.has_genomic_coordinates = raw_data['entries'][0]['fields']['has_genomic_coordinates'][0]
        self.has_go_annotations = raw_data['entries'][0]['fields']['has_go_annotations'][0]
        self.has_interacting_proteins = raw_data['entries'][0]['fields']['has_interacting_proteins'][0]
        self.has_interacting_rnas = raw_data['entries'][0]['fields']['has_interacting_rnas'][0] if len(raw_data['entries'][0]['fields']['has_interacting_rnas']) > 0 else None
        self.has_secondary_structure = raw_data['entries'][0]['fields']['has_secondary_structure'][0]
        self.interacting_proteins = raw_data['entries'][0]['fields']['interacting_protein']
        self.interacting_rnas = raw_data['entries'][0]['fields']['interacting_rna']
        self.length = raw_data['entries'][0]['fields']['length'][0]
        self.product = raw_data['entries'][0]['fields']['interacting_protein']
        self.rfam_family_name = raw_data['entries'][0]['fields']['rfam_family_name']
        self.rfam_id = raw_data['entries'][0]['fields']['rfam_id']
        self.rfam_count = len(self.rfam_id)
        self.rna_type = raw_data['entries'][0]['fields']['rna_type'][0]
        self.species = raw_data['entries'][0]['fields']['species'][0] if len(raw_data['entries'][0]['fields']['species']) > 0 else ''


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
        url = '{endpoint}?query={urs}*&format=json'.format(
            urs=urs,
            endpoint=self.endpoint
        )
        try:
            data = requests.get(url)
            return data.json()['hitCount']
        except:
            return 1
