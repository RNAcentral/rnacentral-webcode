"""
	Selenium functional tests.

    The script does not rely on Django in order to avoid
    creating test databases and loading initial data.
    However, the program is included in the Django project
    to facilitate project-wide searching and renaming of html elements used for testing.

    Each new view should have corresponding tests.

    Usage:

    # test localhost
    python selenium_tests.py

    # test an RNAcentral instance
    python selenium_tests.py --base-url http://test.rnacentral.org/

"""

import unittest
import re
from selenium import webdriver


class BasePage(object):
    """Prototipe object for all pages."""
    base_url = None
    rnacentral_id_regex = r"(RNS[0-9A-F]{10})"

    def __init__(self, browser):
        self.browser = browser

    def navigate(self):
        self.browser.get(self.url)

    def get_title(self):
    	return self.browser.title


class Homepage(BasePage):
    """RNAcentral home page"""
    url = ""

    def __init__(self, browser):
        BasePage.__init__(self, browser)
        self.url = self.base_url

    def _get_example_ids(self, text):
        """Retrieve RNAcentral ids from some text"""
        rnacentral_ids = set(re.findall(self.rnacentral_id_regex, text))
        return rnacentral_ids

    def get_expert_db_example_ids(self, element_id):
        """
            Each expert database has a number of example entries, which are retrieved
            from the homepage by looking for an element with id in the following format:
                <expert-database>-examples
            E.g.
                mirbase-examples
        """
        example_div = self.browser.find_element_by_id(element_id)
        return self._get_example_ids(example_div.get_attribute("innerHTML"))

    # def get_expert_database_urls(self):
    #     return []


class SequencePage(BasePage):
    """Prototipe object for all types of sequence pages"""
    url = "rna/"

    def __init__(self, browser, unique_id):
        BasePage.__init__(self, browser)
        self.url = self.base_url + self.url + unique_id

    def get_xrefs_table_html(self):
        """Retriev text of the database cross-reference table"""
        return self.browser.find_element_by_id("xrefs-table").text

    def get_own_rnacentral_id(self):
        """Get the RNAcentral id of the same page"""
        match = re.search(self.rnacentral_id_regex, self.get_title())
        if match:
            return match.group(1)
        else:
            raise Exception("Rnacentral id not found in the page title")

    def external_urls_exist(self, expert_db_name):
        """
            External urls may have class names in the following format:
                <expert_db_name>-external-url
            Example:
                mirbase-external-url
        """
        external_urls = self.browser.find_elements_by_class_name(expert_db_name + "-external-url")
        if len(external_urls) > 0:
            return True
        else:
            return False


    # to do: test citation lookup
    # to do: test abstract lookup
    # to do: test svg tree
    # to do: test sunburst


class VegaSequencePage(SequencePage):
    """Sequence page with VEGA xrefs"""

    def gene_and_transcript_is_ok(self):
        """
            Find transcipt and gene info, e.g.:
            Transcript OTTHUMT00000047033 from gene OTTHUMG00000017746
        """
        xrefs_table = self.get_xrefs_table_html()
        match = re.search(r'transcript OTTHUMT\d+ from gene OTTHUMG\d+', xrefs_table)
        return True if match else False

    def alternative_transcripts_is_ok(self):
        # to do
        return True


class TmRNASequencePage(SequencePage):
    """Sequence page with tmRNA Website xrefs"""

    def test_one_piece_tmrna(self):
        # to do
        return True

    def test_two_piece_tmrna(self):
        """Make sure partner tmRNAs link to each other"""
        xrefs_table = self.get_xrefs_table_html()
        match = re.search(r'Two-piece tmRNA partner: ' + self.rnacentral_id_regex, xrefs_table)
        if match:
            original_id = self.get_own_rnacentral_id()
            partner_id = match.group(1)
            partner_page = TmRNASequencePage(self.browser, partner_id)
            partner_page.navigate()
            if original_id in self.browser.page_source:
                return True
            else:
                return False
        else:
            return True

    def test_precursor_tmrna(self):
        # to do
        return True


class MirbaseSequencePage(SequencePage):
    """Sequence page with miRBase xrefs"""
    pass


class SrpdbsequencePage(SequencePage):
    """Sequence page with SRPdb xrefs"""
    pass


class ExpertDbPage(BasePage):
    """Summary page for all expert databases"""
    url = 'expert-databases/'

    def __init__(self, browser):
        BasePage.__init__(self, browser)
        self.url = self.base_url + self.url

    def get_svg_diagram_expert_db_count(self):
        """get the number of rectangles representing expert databases"""
        expert_dbs = self.browser.find_elements_by_tag_name("rect")
        return len(expert_dbs)


class RNAcentralTest(unittest.TestCase):
    """Unit tests entry point"""

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.homepage = Homepage(self.browser)
        self.homepage.navigate()

    def tearDown(self):
        self.browser.close()

    def test_homepage(self):
        homepage = Homepage(self.browser)
        homepage.navigate()
        self.assertIn("RNAcentral", homepage.get_title())

    def test_all_expert_database_page(self):
        expert_dbs_page = ExpertDbPage(self.browser)
        expert_dbs_page.navigate()
        self.assertEqual(expert_dbs_page.get_svg_diagram_expert_db_count(), 19)

    def test_tmrna_website_example_pages(self):
        for example_id in self._get_expert_db_example_ids('tmrna-website-examples'):
            tmrna_page = TmRNASequencePage(self.browser, example_id)
            tmrna_page.navigate()
            self.assertTrue(tmrna_page.test_one_piece_tmrna())
            self.assertTrue(tmrna_page.test_two_piece_tmrna())
            self.assertTrue(tmrna_page.test_precursor_tmrna())

    def test_vega_example_pages(self):
        for example_id in self._get_expert_db_example_ids('vega-examples'):
            vegapage = VegaSequencePage(self.browser, example_id)
            vegapage.navigate()
            self.assertTrue(vegapage.gene_and_transcript_is_ok())
            self.assertTrue(vegapage.alternative_transcripts_is_ok())

    def test_mirbase_example_pages(self):
        for example_id in self._get_expert_db_example_ids('mirbase-examples'):
            mirbase_page = MirbaseSequencePage(self.browser, example_id)
            mirbase_page.navigate()
            self.assertTrue(mirbase_page.external_urls_exist('mirbase'))

    def test_srpdb_example_pages(self):
        for example_id in self._get_expert_db_example_ids('srpdb-examples'):
            mirbase_page = MirbaseSequencePage(self.browser, example_id)
            mirbase_page.navigate()
            self.assertTrue(mirbase_page.external_urls_exist('srpdb'))

    # def test_expert_database_landing_pages(self):
    #     pass

    # def test_genome_browsers_page(self):
    #     pass

    def _get_expert_db_example_ids(self, expert_db_id):
        """Retrieve example RNAcentral ids from the homepage"""
        return self.homepage.get_expert_db_example_ids(expert_db_id)


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename = 'selenium_log.txt', level = logging.DEBUG)

    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    BasePage.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
