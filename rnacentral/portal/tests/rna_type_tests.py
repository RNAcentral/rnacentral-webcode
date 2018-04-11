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

import unittest

from django.test import TestCase
from portal.models import Rna


class GenericRnaTypeTest(TestCase):
    def rna_type_of(self, upi, taxid=None):
        return Rna.objects.\
            get(upi=upi).\
            get_rna_type(taxid=taxid, recompute=True)

    def assertRnaTypeIs(self, description, upi, taxid=None):
        self.assertEquals(description, self.rna_type_of(upi, taxid=taxid))


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


class MouseTests(GenericRnaTypeTest):
    def test_uses_lncrna_over_ncrna(self):
        self.assertRnaTypeIs(
            'lncRNA',
            'URS0000A86584',
            taxid=10090)

    @unittest.expectedFailure
    def test_can_handle_duplicate_information(self):
        self.assertRnaTypeIs(
            'snoRNA',
            'URS00004E52D3',
            taxid=10090)
