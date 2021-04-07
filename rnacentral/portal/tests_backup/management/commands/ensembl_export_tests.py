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

import itertools as it

from django.test import SimpleTestCase

from portal.management.commands.ensembl_export import Exporter
from portal.management.commands.ensembl_export import SimpleXref
from portal.management.commands.ensembl_export import SimpleSequence

from django_performance_testing.queries import QueryBatchLimit
from django_performance_testing.timing import TimeLimit


class BasicTest(SimpleTestCase):

    @property
    def data(self):
        exporter = Exporter(destination='test/files', min=0, max=10)
        structured = it.imap(exporter.structure_data, exporter.get_data())
        return list(structured)

    def test_it_fetches_all_sequences(self):
        assert len(self.data) == 7

    def test_it_builds_correct_entry(self):
        with QueryBatchLimit(write=0, read=10):
            with TimeLimit(total=2):
                assert self.data[0] == SimpleSequence(
                    upi='URS0000000001',
                    taxon_id=77133,
                    description='uncultured bacterium partial 16S ribosomal RNA',
                    rna_type='',
                    seq_short='ATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCGAGCGGTAGAGAGAAGCTTGCTTCTCTTGAGAGCGGCGGACGGGTGAGTAATGCCTAGGAATCTGCCTGGTAGTGGGGGATAACGCTCGGAAACGGACGCTAATACCGCATACGTCCTACGGGAGAAAGCAGGGGACCTTCGGGCCTTGCGCTATCAGATGAGC',
                    seq_long='',
                    md5='6bba097c8c39ed9a0fdf02273ee1c79a',
                    xrefs=[]
                )


class PdbeTest(SimpleTestCase):

    @property
    def data(self):
        self.exporter = Exporter('somewhere.json')
        raw = self.exporter.get_data(
            accession__database='PDBE',
            accession__external_id='1FJG',
            accession__optional_id='A')
        return self.exporter.structure_data(next(raw))

    def test_it_sets_id_to_pdb_and_chain(self):
        with QueryBatchLimit(write=0, read=10):
            with TimeLimit(total=1):
                data = self.data
                print(data)
                assert data ==  SimpleSequence(
                    upi='URS000080E226',
                    taxon_id=274,
                    description='16S rRNA from Thermus thermophilus (PDB 4YZV, chain XA)',
                    rna_type='rRNA',
                    seq_short='TTTGTTGGAGAGTTTGATCCTGGCTCAGGGTGAACGCTGGCGGCGTGCCTAAGACATGCAAGTCGTGCGGGCCGCGGGGTTTTACTCCGTGGTCAGCGGCGGACGGGTGAGTAACGCGTGGGTGACCTACCCGGAAGAGGGGGACAACCCGGGGAAACTCGGGCTAATCCCCCATGTGGACCCGCCCCTTGGGGTGTGTCCAAAGGGCTTTGCCCGCTTCCGGATGGGCCCGCGTCCCATCAGCTAGTTGGTGGGGTAATGGCCCACCAAGGCGACGACGGGTAGCCGGTCTGAGAGGATGGCCGGCCACAGGGGCACTGAGACACGGGCCCCACTCCTACGGGAGGCAGCAGTTAGGAATCTTCCGCAATGGGCGCAAGCCTGACGGAGCGACGCCGCTTGGAGGAAGAAGCCCTTCGGGGTGTAAACTCCTGAACCCGGGACGAAACCCCCGACGAGGGGACTGACGGTACCGGGGTAATAGCGCCGGCCAACTCCGTGCCAGCAGCCGCGGTAATACGGAGGGCGCGAGCGTTACCCGGATTCACTGGGCGTAAAGGGCGTGTAGGCGGCCTGGGGCGTCCCATGTGAAAGACCACGGCTCAACCGTGGGGGAGCGTGGGATACGCTCAGGCTAGACGGTGGGAGAGGGTGGTGGAATTCCCGGAGTAGCGGTGAAATGCGCAGATACCGGGAGGAACGCCGATGGCGAAGGCAGCCACCTGGTCCACCCGTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACCGGATTAGATACCCGGGTAGTCCACGCCCTAAACGATGCGCGCTAGGTCTCTGGGTCTCCTGGGGGCCGAAGCTAACGCGTTAAGCGCGCCGCCTGGGGAGTACGGCCGCAAGGCTGAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGAAGCAACGCGAAGAACCTTACCAGGCCTTGACATGCTAGGGAACCCGGGTGAAAGCCTGGGGTGCCCCGCGAGGGGAGCCCTAGCACAGGTGCTGCATGGCCGTCGTCAGCTCGTGCCGTGAGGTGTTGGGTTAAGTCCCGCAACGAGCGCAACCCCCGCCGTTAGTTGCCAGCGGTTCGGCCGGGCACTCTAACGGGACTGCCCGCGAAAGCGGGAGGAAGGAGGGGACGACGTCTGGTCAGCATGGCCCTTACGGCCTGGGCGACACACGTGCTACAATGCCCACTACAAAGCGATGCCACCCGGCAACGGGGAGCTAATCGCAAAAAGGTGGGCCCAGTTCGGATTGGGGTCTGCAACCCGACCCCATGAAGCCGGAATCGCTAGTAATCGCGGATCAGCCATGCCGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACGCCATGGGAGCGGGCTCTACCCGAAGTCGCCGGGAGCCTACGGGCAGGCGCCGAGGGTAGGGCCCGTGACTGGGGCGAAGTCGTAACAAGGTAGCTGTACCGGAAGGTGCGGCTGGATCACCTCCTTTCT',
                    seq_long='',
                    md5='8c29ac94fb1a187b14036d4f9cbc9d83',
                    xrefs=[SimpleXref(external_id='1FJG',
                                      optional_id='A',
                                      database='PDBe',
                                      molecule_type='')]
                )
                assert data.xrefs[0].id == '1FJG_A'
