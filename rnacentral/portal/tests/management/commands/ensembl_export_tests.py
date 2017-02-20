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
        exporter = Exporter(destination='test/files', test=True)
        structured = it.imap(exporter.structure_data, exporter.get_data())
        return list(structured)

    def test_it_fetches_all_sequences(self):
        assert len(self.data) == 32

    def test_it_builds_correct_entry(self):
        with QueryBatchLimit(write=0, read=1):
            with TimeLimit(total=1):
                assert self.data[1] == SimpleSequence(
                    upi='URS0000000004',
                    taxon_id=77133,
                    description='uncultured bacterium partial 16S ribosomal RNA',
                    rna_type='',
                    seq_short='CACGCAGGCGGTTCTGCGCGTTTCGAGTGACAGCGGGCGGCTTACCTGCCCGAGTATTCGAAAGACGGTAGGACTTGAGGGCCAGAGAGGGACACGGAATTCCGGGTGGAGTGGTGAAATGCGTAGAGATCCGGAGGAACACCGAAGGCGAAGGCAGTGTCCTGGCTGGTGACTGACGCTGAGGTGCGAAAGCCGAGGGGAGCGAACGGGATTAGATACCCCGGTAGTCCTGGCCGTAAACGATGACCACCAGGTGTGGGAGGTATCGACCCCTTCGTGCCGGAGTCAACACACTAAGTGGTCCGCCTGGGGATACGGTCGCAAGATTAAAA',
                    seq_long='',
                    md5='030c78be0f492872b95219d172e0c658',
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
        with QueryBatchLimit(write=0, read=1):
            with TimeLimit(total=1):
                data = self.data
                assert data == SimpleSequence(
                    upi='URS000080E226',
                    taxon_id=274,
                    description=u'16S rRNA from Thermus thermophilus (PDB 4YZV, chain XA)',
                    rna_type='rRNA',
                    seq_short='TTTGTTGGAGAGTTTGATCCTGGCTCAGGGTGAACGCTGGCGGCGTGCCTAAGACATGCAAGTCGTGCGGGCCGCGGGGTTTTACTCCGTGGTCAGCGGCGGACGGGTGAGTAACGCGTGGGTGACCTACCCGGAAGAGGGGGACAACCCGGGGAAACTCGGGCTAATCCCCCATGTGGACCCGCCCCTTGGGGTGTGTCCAAAGGGCTTTGCCCGCTTCCGGATGGGCCCGCGTCCCATCAGCTAGTTGGTGGGGTAATGGCCCACCAAGGCGACGACGGGTAGCCGGTCTGAGAGGATGGCCGGCCACAGGGGCACTGAGACACGGGCCCCACTCCTACGGGAGGCAGCAGTTAGGAATCTTCCGCAATGGGCGCAAGCCTGACGGAGCGACGCCGCTTGGAGGAAGAAGCCCTTCGGGGTGTAAACTCCTGAACCCGGGACGAAACCCCCGACGAGGGGACTGACGGTACCGGGGTAATAGCGCCGGCCAACTCCGTGCCAGCAGCCGCGGTAATACGGAGGGCGCGAGCGTTACCCGGATTCACTGGGCGTAAAGGGCGTGTAGGCGGCCTGGGGCGTCCCATGTGAAAGACCACGGCTCAACCGTGGGGGAGCGTGGGATACGCTCAGGCTAGACGGTGGGAGAGGGTGGTGGAATTCCCGGAGTAGCGGTGAAATGCGCAGATACCGGGAGGAACGCCGATGGCGAAGGCAGCCACCTGGTCCACCCGTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACCGGATTAGATACCCGGGTAGTCCACGCCCTAAACGATGCGCGCTAGGTCTCTGGGTCTCCTGGGGGCCGAAGCTAACGCGTTAAGCGCGCCGCCTGGGGAGTACGGCCGCAAGGCTGAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGAAGCAACGCGAAGAACCTTACCAGGCCTTGACATGCTAGGGAACCCGGGTGAAAGCCTGGGGTGCCCCGCGAGGGGAGCCCTAGCACAGGTGCTGCATGGCCGTCGTCAGCTCGTGCCGTGAGGTGTTGGGTTAAGTCCCGCAACGAGCGCAACCCCCGCCGTTAGTTGCCAGCGGTTCGGCCGGGCACTCTAACGGGACTGCCCGCGAAAGCGGGAGGAAGGAGGGGACGACGTCTGGTCAGCATGGCCCTTACGGCCTGGGCGACACACGTGCTACAATGCCCACTACAAAGCGATGCCACCCGGCAACGGGGAGCTAATCGCAAAAAGGTGGGCCCAGTTCGGATTGGGGTCTGCAACCCGACCCCATGAAGCCGGAATCGCTAGTAATCGCGGATCAGCCATGCCGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACGCCATGGGAGCGGGCTCTACCCGAAGTCGCCGGGAGCCTACGGGCAGGCGCCGAGGGTAGGGCCCGTGACTGGGGCGAAGTCGTAACAAGGTAGCTGTACCGGAAGGTGCGGCTGGATCACCTCCTTTCT',
                    seq_long='',
                    md5='8c29ac94fb1a187b14036d4f9cbc9d83',
                    xrefs=[
                        SimpleXref(external_id=u'1FJG', optional_id=u'A', database=u'PDBe'),
                    ])
                assert data.xrefs[0].id == '1FJG_A'
