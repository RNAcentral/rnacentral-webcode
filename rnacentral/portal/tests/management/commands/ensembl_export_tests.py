import unittest

from django.test import SimpleTestCase

from portal.management.commands.ensembl_export import Exporter
# from portal.management.commands.ensembl_export import SimpleXref
# from portal.management.commands.ensembl_export import SimpleSequence


class BasicTest(SimpleTestCase):

    @unittest.skip("No test data yet")
    def test_it_fetches_all_sequences(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_sets_xref_id_to_external_id(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_sets_xref_database_to_display_name(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_fetches_all_xrefs(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_correctly_groups_all_xrefs(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_sets_correct_rnacentral_id(self):
        self.assertEquals(self.data[0].rnacentral_id, '')

    @unittest.skip("No test data yet")
    def test_it_gets_sequence_when_short(self):
        pass

    @unittest.skip("No test data yet")
    def test_it_gets_sequence_when_long(self):
        pass


class PdbeTest(SimpleTestCase):
    def setUp(self):
        self.exporter = Exporter('somewhere.json')
        raw = self.exporter.get_data(
            accession__database='PDBE',
            accession__external_id='1FJG',
            accession__optional_id='A')
        self.data = self.exporter.structure_data(next(raw))

    def test_it_sets_id_to_pdb_and_chain(self):
        self.assertEquals(len(self.data.xrefs), 1)
        self.assertEqual(self.data.xrefs[0].id, '1FJG_A')
