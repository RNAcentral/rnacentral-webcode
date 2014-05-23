"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

"""
	Selenium functional tests.

    The script does not rely on Django in order to avoid
    creating test databases and loading initial data.
    However, the program is included in the Django project
    to facilitate project-wide searching and renaming of html elements used for testing.

    The tests are designed according to a Page Object pattern,
    where each page has a class responsible for retrieving its elements.
    Each page class has an attribute "url", which should be properly
    initialized in the constructor.

    Usage:

    # test localhost
    python selenium_tests.py

    # test an RNAcentral instance
    python selenium_tests.py --base_url http://test.rnacentral.org/
"""

import unittest
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class BasePage(object):
    """Prototipe object for all pages."""
    base_url = None
    rnacentral_id_regex = r"(URS[0-9A-F]{10})"

    def __init__(self, browser, url=''):
        self.browser = browser
        self.url = self.base_url + url

    def navigate(self):
        self.browser.get(self.url)

    def get_title(self):
        return self.browser.title

    def js_errors_found(self):
        """
            All javascript errors are logged in the JSError attribute
            of the body tag.
        """
        try:
            js_errors = self.browser.find_element_by_xpath('//body[@JSError]')
            return True
        except NoSuchElementException:
            return False

    def get_svg_diagrams(self):
        """Check whether all svg diagrams have been generated"""
        svg = self.browser.find_elements_by_tag_name("svg")
        return len(svg)


class Homepage(BasePage):
    """RNAcentral home page"""

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


class SequencePage(BasePage):
    """Prototipe object for all types of sequence pages"""
    url = "rna/"

    def __init__(self, browser, unique_id):
        BasePage.__init__(self, browser, self.url)
        self.url += unique_id

    def navigate(self):
        super(SequencePage, self).navigate()
        WebDriverWait(self.browser, 120).until(lambda s: s.find_element_by_css_selector("#xrefs-table"))
        WebDriverWait(self.browser, 120).until(lambda s: s.find_element_by_css_selector("#d3-species-tree svg"))

    def get_xrefs_table_html(self):
        """Retrieve text of the database cross-reference table"""
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

    def citations_retrieved(self):
        """
            Click the first citation button on the page and then click on the abstract button.
        """
        timeout = 10
        self.browser.find_element_by_class_name("literature-refs-retrieve").click()
        try:
            result = WebDriverWait(self.browser, timeout).until(lambda s: s.find_element(By.CLASS_NAME, "literature-refs-content").is_displayed())
            if not result:
                raise NoSuchElementException
            try:
                self.browser.find_element_by_class_name("abstract-control").click()
                WebDriverWait(self.browser, timeout).until(lambda s: s.find_element(By.CLASS_NAME, "abstract-text").is_displayed())
            except NoSuchElementException:
                pass  # some citations don't have pubmed ids and don't have abstract buttons
        except:
            logging.warning('Citations not loaded ' + self.browser.current_url)
            return False
        return True


class VegaSequencePage(SequencePage):
    """Sequence page with VEGA xrefs."""

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
    """Sequence page with miRBase xrefs. Add miRBase-specific tests as necessary."""
    pass


class SrpdbsequencePage(SequencePage):
    """Sequence page with SRPdb xrefs. Add SRPdb-specific tests as necessary."""
    pass


class ExpertDatabasesOverviewPage(BasePage):
    """An overview page for all expert databases"""
    url = 'expert-databases/'

    def __init__(self, browser):
        BasePage.__init__(self, browser, self.url)

    def get_expert_db_svg_rect_count(self):
        """get the number of rectangles representing expert databases"""
        expert_dbs = self.browser.find_elements_by_tag_name("rect")
        return len(expert_dbs)


class ExpertDatabaseLandingPage(BasePage):
    """An expert database landing page"""
    url = 'expert-database/'

    def __init__(self, browser, expert_db_id):
        BasePage.__init__(self, browser, self.url)
        self.url += expert_db_id

    def get_svg_diagrams(self):
        """
            Make sure all svg are generated.
            Override the default behavior because of the ajax requests.
        """
        try:
            sunburst = WebDriverWait(self.browser, 5).until(lambda s: s.find_element(By.CSS_SELECTOR, "#d3-species-sunburst svg"))
            seq_dist = WebDriverWait(self.browser, 5).until(lambda s: s.find_element(By.CSS_SELECTOR, "#d3-seq-length-distribution svg"))
        except:
            if not sunburst:
                print 'No sunburst'
            if not seq_dist:
                print 'No seq dist'
            return False
        return True


class GenoverseTestPage(BasePage):
    """A page with an embedded genome browser"""
    url = 'rna/'

    def __init__(self, browser, rnacentral_id):
        BasePage.__init__(self, browser, self.url)
        self.url += rnacentral_id

    def genoverse_ok(self):
        genoverse_button = WebDriverWait(self.browser, 30).until(lambda s: s.find_element(By.CLASS_NAME, "genoverse-xref"))
        genoverse_button.click()
        try:
            WebDriverWait(self.browser, 5).until(lambda s: s.find_element(By.CSS_SELECTOR, "table.genoverse").is_displayed())
        except:
            return False
        return True


class RNAcentralTest(unittest.TestCase):
    """Unit tests entry point"""

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.homepage = Homepage(self.browser)
        self.homepage.navigate()

    def tearDown(self):
        self.browser.close()

    def test_homepage(self):
        page = Homepage(self.browser)
        page.navigate()
        self.assertFalse(page.js_errors_found())
        self.assertIn("RNAcentral", page.get_title())

    def test_all_expert_database_page(self):
        page = ExpertDatabasesOverviewPage(self.browser)
        page.navigate()
        self.assertFalse(page.js_errors_found())
        self.assertEqual(page.get_expert_db_svg_rect_count(), 19)

    def test_tmrna_website_example_pages(self):
        for example_id in self._get_expert_db_example_ids('tmrna-website-examples'):
            page = TmRNASequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.test_one_piece_tmrna())
            self.assertTrue(page.test_two_piece_tmrna())
            self.assertTrue(page.test_precursor_tmrna())

    def test_vega_example_pages(self):
        for example_id in self._get_expert_db_example_ids('vega-examples'):
            page = VegaSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.gene_and_transcript_is_ok())
            self.assertTrue(page.alternative_transcripts_is_ok())

    def test_mirbase_example_pages(self):
        for example_id in self._get_expert_db_example_ids('mirbase-examples'):
            page = MirbaseSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.external_urls_exist('mirbase'))

    def test_srpdb_example_pages(self):
        for example_id in self._get_expert_db_example_ids('srpdb-examples'):
            page = MirbaseSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.external_urls_exist('srpdb'))

    def test_expert_database_landing_pages(self):
        expert_dbs = ['tmrna-website', 'srpdb', 'mirbase', 'vega']
        for expert_db in expert_dbs:
            page = ExpertDatabaseLandingPage(self.browser, expert_db)
            page.navigate()
            self.assertFalse(page.js_errors_found())
            self.assertTrue(page.get_svg_diagrams())

    # def test_long_loading_page(self):
    #     page = SequencePage(self.browser, 'URS00002FA515')
    #     page.navigate()
    #     self._sequence_view_checks(page)

    def test_genoverse_page(self):
        page = GenoverseTestPage(self.browser, 'URS000063A371')
        page.navigate()
        self.assertTrue(page.genoverse_ok())

    def _get_expert_db_example_ids(self, expert_db_id):
        """Retrieve example RNAcentral ids from the homepage"""
        return self.homepage.get_expert_db_example_ids(expert_db_id)

    def _sequence_view_checks(self, page):
        self.assertTrue(page.citations_retrieved())
        self.assertFalse(page.js_errors_found())
        self.assertEqual(page.get_svg_diagrams(), 1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='selenium_log.txt',
                        level=logging.WARNING,
                        filemode='w')

    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    BasePage.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
