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

from django.test import SimpleTestCase
from django_performance_testing.queries import QueryBatchLimit
from django_performance_testing.timing import TimeLimit
from portal.models import Rna
from portal.utils.descriptions import rule_method as rm

__doc__ = """
To run these tests you can simply do:

$ python manage.py test portal.tests.description_tests
"""


class GenericDescriptionTest(SimpleTestCase):
    allow_database_queries = True

    def assertDescriptionIs(self, description, upi, taxid=None):
        seq = Rna.objects.get(upi=upi)
        with QueryBatchLimit(write=0, read=10):
            with TimeLimit(total=50):
                computed = seq.get_description(taxid=taxid, recompute=True)
        self.assertEquals(description, computed)

    def assertDescriptionContains(self, short, upi, taxid=None):
        seq = Rna.objects.get(upi=upi)
        with QueryBatchLimit(write=0, read=10):
            with TimeLimit(total=5):
                description = seq.get_description(taxid=taxid, recompute=True)
        self.assertIn(short, description)


class SimpleDescriptionTests(GenericDescriptionTest):
    def test_handles_bantam(self):
        """
        Descriptions should select a name with 'dme-bantam' in it for the
        precursor and both products.
        """
        self.assertDescriptionContains("dme-bantam", "URS00002F21DA", taxid=7227)
        self.assertDescriptionContains("dme-bantam-3p", "URS00004E9E38", taxid=7227)
        self.assertDescriptionContains("dme-bantam-5p", "URS000055786A", taxid=7227)

    def test_handles_ribozymes(self):
        """
        We should pick a good, not repetitive name for ribozymes.
        """
        pass

    def test_can_handle_trnas(self):
        self.assertDescriptionIs(
            "Escherichia coli tRNA-Pro (CGG)", "URS00001DEEBE", taxid=562
        )

    def test_does_not_truncate_rna_types_incorrectly(self):
        self.assertDescriptionIs("Danio rerio tRNA", "URS0000661037", taxid=7955)


class HumanDescriptionTests(GenericDescriptionTest):
    def test_likes_hgnc_for_human(self):
        self.assertDescriptionIs(
            "Homo sapiens DiGeorge syndrome critical region gene 9 (DGCR9)",
            "URS0000759BEC",
            taxid=9606,
        )

        self.assertDescriptionIs(
            "Homo sapiens STARD4 antisense RNA 1 (STARD4-AS1)",
            "URS00003CE153",
            taxid=9606,
        )

        # NOTE: This is a bit questionable, there are other names which may
        # possibly be better
        self.assertDescriptionIs(
            "Homo sapiens small Cajal body-specific RNA 10 (SCARNA10)",
            "URS0000569A4A",
            taxid=9606,
        )

    def test_uses_ensembl_names(self):
        self.assertDescriptionIs(
            "Homo sapiens long intergenic non-protein coding RNA 1729 (LINC01729)",
            "URS00003BECAC",
            taxid=9606,
        )

    def test_prefers_mirbase_for_mirna_precursor(self):
        self.assertDescriptionIs(
            "Homo sapiens (human) microRNA precursor (hsa-mir-3648-1, hsa-mir-3648-2)",
            "URS000075A546",
            taxid=9606,
        )

        self.assertDescriptionIs(
            "Homo sapiens (human) microRNA precursor (hsa-mir-1302-2, hsa-mir-1302 9 to 11)",
            # 'Homo sapiens (human) microRNA precursor (hsa-mir-1302-2, hsa-mir-1302-9, hsa-mir-1302-10, hsa-mir-1302-11)',
            "URS000075CC93",
            taxid=9606,
        )

    def test_includes_gene_name_for_hgnc(self):
        self.assertDescriptionIs(
            "Homo sapiens HOX transcript antisense RNA (HOTAIR)",
            "URS000075C808",
            taxid=9606,
        )

    def test_will_indicate_several_genes_for_hgnc(self):
        self.assertDescriptionIs(
            # 'Homo sapiens RNA, 5S ribosomal (RNA5S1-8, RNA5S 10-17)',
            "Homo sapiens RNA, 5S ribosomal 1 (RNA5S1-8, RNA5S10-17)",
            "URS00000F9D45",
            taxid=9606,
        )

        self.assertDescriptionIs(
            "Homo sapiens RNA, 45S pre-ribosomal 4 (RNA45S4, RNA45SN1)",
            "URS0000ABD87F",
            taxid=9606,
        )

    def test_it_will_use_hgnc_over_gencode(self):
        self.assertDescriptionIs(
            "Homo sapiens HELLP associated long non-coding RNA (HELLPAR)",
            "URS000019E0CD",
            taxid=9606,
        )

    @pytest.mark.skip()
    def test_uses_snopy_descriptions(self):
        self.assertDescriptionIs(
            "Homo sapiens (human) small nucleolar RNA SNORD118L8",
            "URS00006CE02F",
            taxid=9606,
        )


class ArabidopisDescriptionTests(GenericDescriptionTest):
    def test_likes_lncrnadb_over_ena(self):
        self.assertDescriptionIs(
            "Arabidopsis thaliana (thale cress) Long non-coding antisense RNA COOLAIR",
            "URS000018EB2E",
            taxid=3702,
        )

    def test_uses_ena_if_only_source(self):
        self.assertDescriptionIs(
            "Arabidopsis thaliana (thale cress) tRNA-Met(CAT)",
            "URS00005F4CAF",
            taxid=3702,
        )

    def test_it_uses_most_common_ena_name(self):
        self.assertDescriptionIs(
            "Arabidopsis thaliana (thale cress) partial tRNA-Leu",
            "URS000048B30C",
            taxid=3702,
        )

    def test_uses_rfam_if_only_source(self):
        self.assertDescriptionIs(
            "Arabidopsis thaliana tRNA", "URS00006A2469", taxid=3702
        )

    def test_it_uses_tair_over_refseq(self):
        self.assertDescriptionIs(
            "Arabidopsis thaliana (thale cress) TAS3/TASIR-ARF (TRANS-ACTING SIRNA3); other RNA",
            "URS00003AC4AA",
            taxid=3702,
        )


class MouseDescriptionTests(GenericDescriptionTest):
    @unittest.expectedFailure
    def test_likes_refseq_over_noncode(self):
        """This is failing currently, because Rfam and refseq disagree about
        the rna_type. We end up using Rfam's because that is generally right,
        however, in this case we end up with worse name because of it. Though
        examining the data for the RefSeq annotation I am inclined to believe
        Rfam over RefSeq in this case.
        """
        self.assertDescriptionIs(
            "Mus musculus small Cajal body-specific RNA 1 (Scarna13), guide RNA",
            "URS00006550DA",
            taxid=10090,
        )

    def test_likes_refseq_over_ena(self):
        self.assertDescriptionIs(
            "Mus musculus small nucleolar RNA, C/D box 17 (Snord17), small nucleolar RNA",
            "URS000051DCEC",
            taxid=10090,
        )

        self.assertDescriptionIs(
            "Mus musculus small nucleolar RNA, H/ACA box 3 (Snora3), small nucleolar RNA",
            "URS000060B496",
            taxid=10090,
        )

    def test_will_not_build_using_rfam_if_disagree_rna_type(self):
        # This is a good candidate for using Rfam hits as a source of RNA
        # types. If we did so then this would be a snoRNA and have a different
        # name.
        self.assertDescriptionIs(
            "Mus musculus predicted gene 12238 (Gm12238)", "URS00004E52D3", taxid=10090
        )

    def test_it_will_strip_trailing_terms_from_description(self):
        self.assertDescriptionIs(
            "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA",
            "URS00008E3A1B",
            taxid=10090,
        )

    def test_it_likes_rfam_over_noncode(self):
        self.assertDescriptionIs(
            "Mus musculus small Cajal body-specific RNA 2 (Scarna2)",
            "URS00006B3271",
            taxid=10090,
        )

        # self.assertDescriptionIs(
        #     'Mus musculus Small Cajal body-specific RNA 6',
        #     'URS0000653D5F',
        #     taxid=10090)

    def test_does_not_add_duplicate_gene_names(self):
        self.assertDescriptionIs(
            "Mus musculus predicted gene 29254 (Gm29254)", "URS0000A86584", taxid=10090
        )


class CattleDescriptionTests(GenericDescriptionTest):
    def test_likes_name_with_precursor(self):
        self.assertDescriptionIs(
            "Bos taurus (cattle) microRNA 431 precursor", "URS00007150F8", taxid=9913
        )

    @unittest.skip("No examples yet")
    def test_will_use_gtRNAdb(self):
        pass

    def test_use_pdb_over_rfam(self):
        self.assertDescriptionIs(
            "transfer RNA-Trp from Bos taurus (PDB 2AKE, chain B)",
            "URS0000669B12",
            taxid=9913,
        )

    def test_will_use_mirbase_for_precusors(self):
        self.assertDescriptionIs(
            "Bos taurus (cattle) microRNA bta-mir-497 precursor",
            "URS00006D80BC",
            taxid=9913,
        )

        self.assertDescriptionIs(
            "Bos taurus (cattle) microRNA bta-mir-10a precursor",
            "URS000075CF25",
            taxid=9913,
        )

    def test_likes_refseq_over_ena(self):
        self.assertDescriptionIs(
            "Bos taurus telomerase RNA component (TERC), telomerase RNA",
            "URS00003EBD9A",
            taxid=9913,
        )


class WormTests(GenericDescriptionTest):
    def test_likes_wormbase(self):
        self.assertDescriptionIs(
            "Caenorhabditis elegans long non-coding RNA linc-125",
            "URS00005511ED",
            taxid=6239,
        )

    def test_likes_uses_wormbase_over_good_silva(self):
        self.assertDescriptionIs(
            "Caenorhabditis elegans 26s rRNA", "URS00004FB44B", taxid=6239
        )

    # NOTE: this may be questionable as there is a fairly specific looking name
    # from wormbase, but the one from mirbase looks better to me. Need to see
    # what people in the worm/miRNA field like.
    def test_it_likes_mirbase_over_wormbase(self):
        self.assertDescriptionIs(
            "Caenorhabditis elegans microRNA cel-miR-229-5p",
            "URS0000466DE6",
            taxid=6239,
        )

    def test_likes_wormbase_over_rfam(self):
        self.assertDescriptionIs(
            "Caenorhabditis elegans tRNA-Undet", "URS00006DC8B9", taxid=6239
        )

        self.assertDescriptionIs(
            "Caenorhabditis elegans tRNA-His", "URS000069D7FA", taxid=6239
        )


class LargeDataTests(GenericDescriptionTest):
    @unittest.skip("No examples yet")
    def test_can_compute_when_many_cross_ref(self):
        """This is a stress test to see if this still performs quickly given a
        sequence with many ~10k xrefs
        """
        self.assertDescriptionIs("tRNA from 3413 species", "URS0000181AEC")


def test_can_strip_trailing_dots():
    name = "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA."
    ans = "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA"
    assert rm.remove_extra_description_terms(name) == ans


def test_can_strip_extra_lnc_rna():
    name = "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA"
    ans = "Mus musculus predicted gene 11532 (Gm11532)"
    assert rm.trim_trailing_rna_type("lncRNA", name) == ans


def test_can_strip_extra_lnc_rna_when_antisense():
    name = "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA"
    ans = "Mus musculus predicted gene 11532 (Gm11532)"
    assert rm.trim_trailing_rna_type("antisense", name) == ans


def test_will_not_strip_if_rna_type_differs():
    name = "Mus musculus predicted gene 11532 (Gm11532), long non-coding RNA"
    assert rm.trim_trailing_rna_type("SRP_RNA", name) == name


def test_will_strip_non_coding_term_with_whitespace():
    name = (
        "Mus musculus myocardial infarction associated transcript (non- protein coding)"
    )
    ans = "Mus musculus myocardial infarction associated transcript"
    assert rm.remove_extra_description_terms(name) == ans


def test_will_strip_non_coding_term():
    name = (
        "Mus musculus myocardial infarction associated transcript (non-protein coding)"
    )
    ans = "Mus musculus myocardial infarction associated transcript"
    assert rm.remove_extra_description_terms(name) == ans


def test_will_correct_tmrna():
    name = "Homo sapiens (human) transfer-messenger mRNA Esche_coli_K12"
    ans = "Homo sapiens (human) transfer-messenger RNA Esche_coli_K12"
    assert rm.remove_extra_description_terms(name) == ans
