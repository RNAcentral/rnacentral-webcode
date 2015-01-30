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

    By default the tests use Firefox, but one can use a headless PhantomJS
    browser (http://phantomjs.org/) as an alternative.

    Usage:

    # test localhost
    python selenium_tests.py

    # test an RNAcentral instance
    python selenium_tests.py --base_url http://test.rnacentral.org/

    # test an RNAcentral instance using PhantomJS
    python selenium_tests.py --base_url http://test.rnacentral.org/ --driver=phantomjs
"""

import unittest
import random
import re
import sys
import time
import urllib
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
                citations_loaded = WebDriverWait(self.browser, timeout).until(lambda s: s.find_element_by_class_name("abstract-control").is_displayed())
                self.browser.find_element_by_class_name("abstract-control").click()
                WebDriverWait(self.browser, timeout).until(lambda s: s.find_element(By.CLASS_NAME, "abstract-text"))
            except NoSuchElementException:
                pass  # some citations don't have pubmed ids and don't have abstract buttons
        except:
            logging.warning('Citations not loaded ' + self.browser.current_url)
            return False
        return True


class TaxidFilteringSequencePage(SequencePage):
    """
    Class for testing sequence page customization based on taxid.
    """

    def get_info_text(self):
        """
        """
        info_box = self.browser.find_element_by_class_name('well')
        return info_box.text

    def get_page_subtitle(self):
        """
        Page subtitle is either the name of the species or the number of species.
        """
        subtitle = self.browser.find_element_by_css_selector('h1 small')
        return subtitle.text

    def get_warning_info_text(self):
        """
        When a taxid from the url doesn't match any annotations, a warning should be displayed.
        """
        warning = self.browser.find_element_by_class_name('alert-danger')
        return warning.text

    def get_species_from_xref_table(self):
        """
        When taxid filtering is enabled, the xref table should have annotations
        only from one species.
        """
        tds = self.browser.find_elements_by_css_selector('#xrefs-table td')
        species = [x.text for x in tds[2::3]] #3, 6, 9 etc tds
        return set(species)


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
    """Sequence page with miRBase xrefs. Add miRBase-specific tests here."""
    pass


class SrpdbSequencePage(SequencePage):
    """Sequence page with SRPdb xrefs. Add SRPdb-specific tests here."""
    pass


class RefseqSequencePage(SequencePage):
    """Sequence page with RefSeq xrefs. Add RefSeq-specific tests here."""
    pass


class RdpSequencePage(SequencePage):
    """Sequence page with Rdp xrefs. Add RefSeq-specific tests here."""
    pass


class ExpertDatabasesOverviewPage(BasePage):
    """An overview page for all expert databases"""
    url = 'expert-databases/'

    def __init__(self, browser):
        BasePage.__init__(self, browser, self.url)

    def get_expert_tr_count(self):
        """get the number of rows representing expert databases"""
        expert_dbs = self.browser.find_elements_by_tag_name("tr")
        return len(expert_dbs)

    def get_footer_expert_db_count(self):
        """get the number of expert database links in the footer"""
        expert_dbs = self.browser.find_elements_by_css_selector('#global-footer .col-md-7 li>a')
        return len(expert_dbs)


class ExpertDatabaseLandingPage(BasePage):
    """An expert database landing page"""
    url = 'expert-database/'

    def __init__(self, browser, expert_db_id):
        BasePage.__init__(self, browser, self.url)
        self.url += expert_db_id
        self.expert_db_id = expert_db_id

    def get_svg_diagrams(self):
        """
            Make sure all svg are generated.
            Override the default behavior because of the ajax requests.
        """
        NO_SUNBURST = ['ena', 'rfam']
        NO_SEQ_DIST = ['lncrnadb']
        try:
            if self.expert_db_id not in NO_SUNBURST:
                sunburst = self.browser.find_element(By.CSS_SELECTOR, "#d3-species-sunburst svg")
            if self.expert_db_id not in NO_SEQ_DIST:
                seq_dist = self.browser.find_element(By.CSS_SELECTOR, "#d3-seq-length-distribution svg")
        except:
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


class MetaSearchPage(BasePage):
    """
    Can be any page because the search box is in the site-wide header.
    """
    url = ''

    def __init__(self, browser, query_url=''):
        BasePage.__init__(self, browser, self.url)
        self.url += query_url
        self.page_size = 15

    def get_metasearch_results(self):
        """
        Get results as an array of list elements.
        """
        return WebDriverWait(self.browser, 30).until(
                lambda s: s.find_elements(By.CLASS_NAME, "result"))

    def test_example_searches(self):
        """
        Click on example searches in the header and make sure there are results.
        """

        def click_load_more():
            """
            Click the Load more button and verify the number of results.
            """
            load_more = WebDriverWait(self.browser, 30).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'load-more')
                )
            )
            for i in [2, 3, 4]:
                load_more.click()
                WebDriverWait(self.browser, 5).until(
                    EC.text_to_be_present_in_element(
                        (By.ID, "metasearch-results-count"),
                        '%i out of ' % (i * self.page_size)
                    )
                )

        def enable_facet():
            """
            Select a facet at random and enable it. Make sure that the results
            are filtered correctly.
            """
            facet_link = WebDriverWait(self.browser, 5).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "metasearch-facet-link")
                )
            )
            # get the number of entries in the facet
            facet_count = re.search(r'\((.+?)\)$', facet_link.text)
            facet_link.click()
            WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "metasearch-results-count"),
                    'out of %s' % facet_count.group(1)
                )
            )

        success = []
        self.browser.maximize_window() # sometimes phantomjs cannot find elements without this
        examples = self.browser.find_elements_by_css_selector('.example-searches a')
        for example in examples:
            results = []
            example.click()
            click_load_more()
            enable_facet()
            results = self.get_metasearch_results()
            if len(results) > 0:
                success.append(1)
        return len(success) == len(examples)

    def _submit_search(self, query):
        search_box = self.browser.find_element_by_css_selector('.rnacentral-masthead input')
        search_box.send_keys(query)
        search_button = self.browser.find_element_by_css_selector('.rnacentral-masthead button')
        # submit either by hitting Enter or clicking Submit
        if random.randint(1, 2) == 1:
            search_button.click()
        else:
            search_box.send_keys(Keys.RETURN)

    def warnings_present(self):
        """
        div.metasearch-no-results is only generated when a search returns
        zero results. This test makes sure that the element is present and
        displayed.
        """
        try:
            warning = WebDriverWait(self.browser, 5).until(lambda s: s.find_element(By.CLASS_NAME, "metasearch-no-results"))
            return warning.is_displayed()
        except:
            return False


class RNAcentralTest(unittest.TestCase):
    """Unit tests entry point"""
    driver = 'firefox'

    def setUp(self):
        if self.driver == 'firefox':
            self.browser = webdriver.Firefox()
        elif self.driver == 'phantomjs':
            self.browser = webdriver.PhantomJS()
        else:
            sys.exit('Driver not found')
        self.homepage = Homepage(self.browser)
        self.homepage.navigate()

    def tearDown(self):
        self.browser.close()

    def test_homepage(self):
        page = Homepage(self.browser)
        page.navigate()
        self.assertFalse(page.js_errors_found())
        self.assertIn("RNAcentral", page.get_title())

    def test_browser_back_button(self):
        """
        Make sure browser history is recorded correctly.
        """
        history = ['contact', 'downloads', 'search?q=mirbase',
                   'search?q=foobar']
        page = MetaSearchPage(self.browser)
        for item in history:
            page.browser.get(page.base_url + item)
            time.sleep(2)
        for item in reversed(history):
            self.assertIn(urllib.quote(item), urllib.quote(page.browser.current_url))
            page.browser.back()

    def test_metasearch_examples(self):
        """
        Test metasearch examples, can be done on any page.
        """
        page = MetaSearchPage(self.browser)
        page.navigate()
        self.assertTrue(page.test_example_searches())

    def test_metasearch_no_results(self):
        """
        Run a metasearch query that won't find any results, make sure that
        no results are displayed.
        """
        page = MetaSearchPage(self.browser)
        page.navigate()
        query = 'Foo bar baz'
        page._submit_search(query)
        self.assertTrue(page.warnings_present())

    def test_metasearch_no_warnings(self):
        """
        Run a metasearch query that will find results, make sure that some
        results are displyaed. The opposite of `test_metasearch_no_results`.
        """
        page = MetaSearchPage(self.browser)
        page.navigate()
        query = 'RNA'
        page._submit_search(query)
        self.assertFalse(page.warnings_present())

    def test_metasearch_grouping_operators(self):
        """
        Test a query with logical operators and query grouping.
        """
        page = MetaSearchPage(self.browser)
        page.navigate()
        query = '(expert_db:"mirbase" OR expert_db:"lncrnadb") NOT expert_db:"rfam"'
        page._submit_search(query)
        self.assertTrue(len(page.get_metasearch_results()) > 0)

    def test_metasearch_load_search_url(self):
        """
        Load a metadata search using a search url.
        """
        page = MetaSearchPage(self.browser, 'search?q=mirbase')
        page.navigate()
        self.assertTrue(len(page.get_metasearch_results()) > 0)

    def test_metasearch_species_specific_filtering(self):
        """
        Make sure that URS/taxid and URS_taxid are found in metadata search.
        """
        # forward slash
        page = MetaSearchPage(self.browser, 'search?q=URS000047C79B/9606')
        page.navigate()
        self.assertEqual(len(page.get_metasearch_results()), 1)
        # underscore
        page = MetaSearchPage(self.browser, 'search?q=URS000047C79B_9606')
        page.navigate()
        self.assertEqual(len(page.get_metasearch_results()), 1)
        # non-existing taxid
        page = MetaSearchPage(self.browser, 'search?q=URS000047C79B_00000')
        page.navigate()
        self.assertTrue(page.warnings_present())

    def test_all_expert_database_page(self):
        page = ExpertDatabasesOverviewPage(self.browser)
        page.navigate()
        self.assertFalse(page.js_errors_found())
        self.assertEqual(page.get_expert_tr_count(), page.get_footer_expert_db_count())

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

    def test_refseq_example_pages(self):
        for example_id in self._get_expert_db_example_ids('refseq-examples'):
            page = RefseqSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)

    def test_rdp_example_pages(self):
        for example_id in self._get_expert_db_example_ids('rdp-examples'):
            page = RdpSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)

    def test_mirbase_example_pages(self):
        for example_id in self._get_expert_db_example_ids('mirbase-examples'):
            page = MirbaseSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.external_urls_exist('mirbase'))

    def test_srpdb_example_pages(self):
        for example_id in self._get_expert_db_example_ids('srpdb-examples'):
            page = SrpdbSequencePage(self.browser, example_id)
            page.navigate()
            self._sequence_view_checks(page)
            self.assertTrue(page.external_urls_exist('srpdb'))

    def test_expert_database_landing_pages(self):
        expert_dbs = ['tmrna-website', 'srpdb', 'mirbase', 'vega',
                      'ena', 'rfam', 'lncrnadb', 'gtrnadb', 'refseq', 'rdp']
        for expert_db in expert_dbs:
            page = ExpertDatabaseLandingPage(self.browser, expert_db)
            page.navigate()
            self.assertFalse(page.js_errors_found())
            self.assertTrue(page.get_svg_diagrams())

    def test_xref_pagination(self):
        """
        Test xref table pagination.
        """
        class XrefPaginationPage(SequencePage):
            """
            Get the active xref page number.
            """
            def get_active_xref_page_num(self):
                active_button = self.browser.find_element_by_css_selector('li.active>a.xref-pagination')
                return active_button.text

        upi = 'URS00006EC23D'
        xref_page_num = '5'
        page = XrefPaginationPage(self.browser, upi + '?xref-page=' + xref_page_num)
        page.navigate()
        self.assertTrue(page.get_active_xref_page_num(), xref_page_num)
        self._sequence_view_checks(page)

    def test_genoverse_page(self):
        page = GenoverseTestPage(self.browser, 'URS00000B15DA')
        page.navigate()
        self.assertTrue(page.genoverse_ok())

    def test_taxid_filtering_off(self):
        page = TaxidFilteringSequencePage(self.browser, 'URS000047C79B')
        page.navigate()
        self.assertTrue(re.match('\d+ species', page.get_page_subtitle()))
        self.assertIn('This unique sequence was observed in multiple species', page.get_info_text())

    def test_taxid_filtering_on(self):
        taxid = {'species': 'Homo sapiens', 'ncbi_id': '9606'}
        page = TaxidFilteringSequencePage(self.browser, 'URS000047C79B' + '/' + taxid['ncbi_id'])
        page.navigate()
        species = page.get_species_from_xref_table()
        self.assertEqual(len(species), 1)
        self.assertEqual(species.pop(), taxid['species'])
        self.assertEqual(page.get_page_subtitle(), taxid['species'])
        self.assertIn('Showing annotations from ' + taxid['species'], page.get_info_text())

    def test_taxid_filtering_spurious_taxid(self):
        """
        When a taxid is not found, the url is redirected
        to a non-species-specific id.
        """
        page = TaxidFilteringSequencePage(self.browser, 'URS000047C79B' + '/' + '0'*10)
        page.navigate()
        self.assertIn('No annotations from taxid', page.get_warning_info_text())

    def test_taxid_filtering_with_underscore(self):
        page = TaxidFilteringSequencePage(self.browser, 'URS00000B15DA_9606')
        page.navigate()
        self.assertEqual(page.get_page_subtitle(), 'Homo sapiens')

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
    parser.add_argument('--driver', default='firefox',
                        choices=['firefox', 'phantomjs'])
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    BasePage.base_url = args.base_url
    RNAcentralTest.driver = args.driver

    sys.argv[1:] = args.unittest_args
    unittest.main()
