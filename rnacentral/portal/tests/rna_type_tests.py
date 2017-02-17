from django.test import TestCase
from portal.models import Rna


class GenericRnaTypeTest(TestCase):
    def rna_type_of(self, upi, taxid=None):
        return Rna.objects.\
            get(upi=upi).\
            get_rna_type(taxid=taxid, recompute=True)

    def assertRnaTypeIs(self, description, upi, taxid=None):
        self.assertEquals(description, self.description_of(upi, taxid=taxid))


class WormTests(GenericRnaTypeTest):
    def test_gets_mirna_over_pirna(self):
        self.assertRnaTypeIs(
            'miRNA',
            'URS0000016972',
            taxid=6239)


class HumanTests(GenericRnaTypeTest):
    def test_if_has_both_anti_and_lnc_likes_lnc(self):
        self.assertRnaTypeIs(
            'lncRNA',
            'URS0000732D5D',
            taxid=9606)
