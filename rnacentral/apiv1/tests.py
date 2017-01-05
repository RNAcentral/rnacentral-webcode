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

"""
API v1 tests

Usage:

# test localhost
python apiv1/tests.py

# test RNAcentral server
python apiv1/tests.py --base_url http://test.rnacentral.org/
python apiv1/tests.py --base_url http://rnacentral.org/
"""

import argparse
import django
import math
import os
import unittest
import requests
import sys
import time
import xml.dom.minidom
from random import randint


class ApiV1BaseClass(unittest.TestCase):
    """
    Base class for API tests.
    """
    base_url = ''
    api_url = 'api/v1/'

    upi = 'URS0000000001'
    upi_with_genomic_coordinates = 'URS00000B15DA'
    md5 = '6bba097c8c39ed9a0fdf02273ee1c79a' # URS0000000001
    accession = 'Y09527.1:2562..2627:tRNA'
    timeout = 60 # seconds

    def _get_api_url(self, extra=''):
        """
        Construct a valid API url.
        """
        return ''.join([self.base_url, self.api_url, extra])

    def _test_url(self, url):
        """
        Auxiliary function for testing the API with and without trailing slash.
        """
        # remove the trailing slash if present
        if url[-1] == '/':
            url = url[:-1]
        # test without the slash
        start = time.time()
        r = requests.get(url)
        end = time.time()
        self.assertTrue(end - start < self.timeout)
        self.assertEqual(r.status_code, 200)
        # add the slash back if there are no url parameters
        if '?' not in url:
            url += '/'
            r = requests.get(url)
            self.assertEqual(r.status_code, 200)
        return r.json()


class BasicEndpointsTestCase(ApiV1BaseClass):
    """
    Basic tests for generic endpoints.
    """
    def test_current_api_endpoint(self):
        """
        Stable endpoint for the latest version of the API.
        """
        url = self.base_url + 'api/current'
        self._test_url(url)

    def test_api_v1_endpoint(self):
        """
        Test API v1 endpoint.
        """
        url = self._get_api_url()
        self._test_url(url)


class AccessionEndpointsTestCase(ApiV1BaseClass):
    """
    Test Accession endpoints.
    * /accession/id/info
    * /accession/id/citations
    """
    def test_accession_entry(self):
        """
        Test accession info endpoint.
        """
        url = self._get_api_url('accession/%s/info' % self.accession)
        self._test_url(url)

    def test_accession_citations(self):
        """
        Test accession citations endpoint.
        """
        url = self._get_api_url('accession/%s/citations' % self.accession)
        self._test_url(url)


class RnaEndpointsTestCase(ApiV1BaseClass):
    """
    Test RNA endpoints
    * /rna
    * /rna/id/xrefs
    * /rna/id/publications
    """
    def test_rna_list(self):
        """
        Test RNA list (hyperlinked response).
        """
        url = self._get_api_url('rna')
        self._test_url(url)

    def test_rna_list_pagination(self):
        """
        Test paginated RNA list (hyperlinked response).
        """
        page = 10
        page_size = 5
        url = self._get_api_url('rna/?page=%i&page_size=%i' % (page, page_size))
        data = self._test_url(url)
        self.assertEqual(len(data['results']), page_size)

    def test_rna_sequence(self):
        """
        Test RNA entry (hyperlinked response).
        """
        url = self._get_api_url('rna/%s/' % self.upi)
        data = self._test_url(url)
        self.assertEqual(data['md5'], self.md5)
        self.assertEqual(data['length'], 200)

    def test_rna_xrefs(self):
        """
        Test RNA xrefs endpoint.
        """
        url = self._get_api_url('rna/%s/xrefs' % self.upi)
        self._test_url(url)

    def test_rna_publications(self):
        """
        Test RNA publications endpoint.
        """
        url = self._get_api_url('rna/%s/publications' % self.upi)
        data = self._test_url(url)
        self.assertEqual(len(data['results']), 2)

    def test_xref_pagination(self):
        """
        Ensure that xrefs can be paginated.
        """
        upi = 'URS0000004483' # >150 xrefs
        page = 7
        page_size = 2
        url = self._get_api_url('rna/{upi}/xrefs?page={page}&page_size={page_size}'.format(
            upi=upi, page=page, page_size=page_size))
        data = self._test_url(url)
        self.assertTrue(len(data['results']), page_size)


class NestedXrefsTestCase(ApiV1BaseClass):
    """
    Test flat/hyperlinked pagination.
    """
    def test_hyperlinked_responses(self):
        """
        Test hyperlinked response explicitly specified in the url.
        """
        url = self._get_api_url('rna?flat=false')
        data = self._test_url(url)
        self.assertIn('http', data['results'][0]['xrefs'])

    def test_flat_response(self):
        """
        Test flat response explicitly specified in the url.
        """
        url = self._get_api_url('rna/%s%s' % (self.upi, '?flat=true'))
        data = self._test_url(url)
        self.assertNotEqual(len(data['xrefs']), 0)

    def test_large_nested_rna(self):
        """
        For nested responses only a subset of xrefs is included
        in the original response and the rest can be paginated
        in separate requests.
        """
        upi = 'URS000065859A' # >200,000 xrefs
        url = self._get_api_url('rna/%s?flat=true' % upi)
        data = self._test_url(url)
        self.assertTrue(data['xrefs']['count'] > 200000)
        self.assertTrue(len(data['xrefs']) < 1000)

    def test_large_nested_page(self):
        """
        Ensure that xrefs can be paginated.
        """
        page = 115
        page_size = 100
        url = self._get_api_url('rna?page={page}&page_size={page_size}&flat=true'.format(
            page=page, page_size=page_size))
        data = self._test_url(url)
        self.assertTrue(len(data['results']), page_size)


class OutputFormatsTestCase(ApiV1BaseClass):
    """
    Test output formats.
    """
    def test_json_yaml_api_formats(self):
        """
        Test json/yaml/api formats.
        """
        formats = {'json': 'application/json',
                   'yaml': 'application/yaml',
                   'api': 'text/html'}
        targets = ('rna', 'rna/%s' % self.upi,
                   'rna/%s/xrefs' % self.upi,
                   'accession/%s/info' % self.accession,
                   'accession/%s/citations' % self.accession)
        self._output_format_tester(formats, targets)

    def test_fasta_output(self):
        """
        Test fasta format.
        """
        formats = {'fasta': 'text/fasta'}
        targets = ('rna', 'rna/%s' % self.upi)
        self._output_format_tester(formats, targets)

    def test_gff_output(self):
        """
        Test gff output.
        """
        formats = {'gff': 'text/gff'}
        targets = ('rna/%s' % self.upi_with_genomic_coordinates,)
        # test response status codes
        self._output_format_tester(formats, targets)
        # further check the gff text output
        r = requests.get(self._get_api_url(targets[0]+'.gff'))
        self.assertIn('exon', r.text)
        # test a sequence without genomic coordinates
        r = requests.get(self._get_api_url('rna/%s.gff' % self.upi))
        self.assertIn('# Genomic coordinates not available', r.text)

    def test_gff3_output(self):
        """
        Test gff3 output.
        """
        formats = {'gff3': 'text/gff3'}
        targets = ('rna/%s' % self.upi_with_genomic_coordinates,)
        # test response status codes
        self._output_format_tester(formats, targets)
        # further check the gff text output
        r = requests.get(self._get_api_url(targets[0]+'.gff3'))
        self.assertIn('noncoding_exon', r.text)
        # test a sequence without genomic coordinates
        r = requests.get(self._get_api_url('rna/%s.gff3' % self.upi))
        self.assertIn('# Genomic coordinates not available', r.text)

    def test_bed_output(self):
        """
        Test bed output.
        """
        formats = {'bed': 'text/bed'}
        targets = ('rna/%s' % self.upi_with_genomic_coordinates,)
        # test response status codes
        self._output_format_tester(formats, targets)
        # further check the gff text output
        r = requests.get(self._get_api_url(targets[0]+'.bed'))
        self.assertIn(self.upi_with_genomic_coordinates, r.text)
        # test a sequence without genomic coordinates
        r = requests.get(self._get_api_url('rna/%s.bed' % self.upi))
        self.assertIn('# Genomic coordinates not available', r.text)

    def _output_format_tester(self, formats, targets):
        """
        Test all possible ways of specifying output format:
        * suffix, e.g. ".json"
        * url notation, e.g. "?format=json"
        * accept headers
        """
        urls = [self._get_api_url(x) for x in targets]
        for url in urls:
            for suffix, headers in formats.iteritems():
                r = requests.get(url + '.%s' % suffix) # format suffix
                self.assertEqual(r.status_code, 200, url)
                r = requests.get(url + '?format=%s' % suffix) # url notation
                self.assertEqual(r.status_code, 200, url)
                r = requests.get(url, headers={"Accept": headers}) # accept headers
                self.assertEqual(r.status_code, 200, url)

    def test_genome_annotations(self):
        """
        Test the Ensembl-like endpoint for retrieving data
        based on genome coordinates.
        `feature` was replaced with `overlap` in Ensembl.
        """
        targets = [
            'feature/region/homo_sapiens/Y:25,183,643-25,184,773',
            'overlap/region/homo_sapiens/2:39,745,816-39,826,679',
        ]
        for target in targets:
            url = self._get_api_url(target)
            data = self._test_url(url)
            self.assertNotEqual(len(data), 0)
            for annotation in data:
                if annotation['feature_type'] == 'transcript':
                    self.assertIn('URS', annotation['external_name'])
                elif annotation['feature_type'] == 'exon':
                    self.assertIn('URS', annotation['Parent'])
                else:
                    self.assertEqual(0, 1, "Unknown genomic annotation type")


class FiltersTestCase(ApiV1BaseClass):
    """
    Test url parameter filters.
    """
    def test_rna_md5_filter(self):
        """
        Test md5 filter.
        """
        url = self._get_api_url('rna/?md5=%s' % self.md5)
        data = self._test_url(url)
        self.assertEqual(data['results'][0]['rnacentral_id'], self.upi)

    def test_rna_upi_filter(self):
        """
        Test filtering by RNAcentral id.
        """
        url = self._get_api_url('rna/?upi=%s' % self.upi)
        data = self._test_url(url)
        self.assertEqual(data['results'][0]['md5'], self.md5)

    def test_rna_length_filter(self):
        """
        Test filtering by sequence length.
        """
        filter_tests = [
            'rna/?min_length=200000',
            'rna/?length=2014',
            'rna/?max_length=11',
            'rna/?min_length=11&max_length=12',
        ]
        for filter_test in filter_tests:
            url = self._get_api_url(filter_test)
            data = self._test_url(url)
            self.assertNotEqual(data['count'], 0)

    def test_rna_database_filter(self):
        """
        Test filtering by database name.
        """
        for database in Database.objects.all():
            if database.name in ['ENA', 'Rfam']:
                continue # skip large databases
            url = self._get_api_url('rna/?database=%s' % database.label)
            data = self._test_url(url)
            self.assertNotEqual(data['count'], 0)

    def test_non_existing_database_filter(self):
        """
        Test filtering by database name when the database
        name does not exist.
        """
        url = self._get_api_url('rna/?database=test')
        data = self._test_url(url)
        self.assertEqual(data['count'], 0)

    def test_rna_external_id_filter(self):
        """
        Test filtering by external id.
        """
        external_ids = [
            'Stap.epid._AF269831', # SRPDB
            'MIMAT0000091', # miRBase
            'OTTHUMG00000172092', # Vega
            'Lepto_inter_Lai566', # tmRNA Website
            '1J5E', # PDB
            'NR_029645', # RefSeq
        ]
        for external_id in external_ids:
            url = self._get_api_url('rna?external_id=' + external_id)
            data = self._test_url(url)
            self.assertNotEqual(data['count'], 0, 'Failed on %s' % url)


class RandomEntriesTestCase(ApiV1BaseClass):
    """
    Test entries at random.
    """
    def test_random_api_sequences(self):
        """
        Test random API entries.
        """
        num_tests = 10
        rna_count = Rna.objects.count()
        for _ in xrange(num_tests):
            rna = Rna.objects.only('upi').get(id=randint(1, rna_count))
            url = self._get_api_url('rna/%s?flat=true' % rna.upi)
            start = time.time()
            r = requests.get(url)
            end = time.time()
            msg = 'Failed on %s' % url
            self.assertEqual(r.status_code, 200, msg)
            self.assertTrue(end - start < self.timeout, msg)

    def test_random_api_pages(self):
        """
        Test random large paginated responses.
        """
        num_tests = 5
        page_size = 100
        rna_count = Rna.objects.count()
        num_pages = math.trunc(rna_count/page_size)
        for _ in xrange(num_tests):
            page = randint(1, num_pages)
            url = self._get_api_url('rna?flat=true&page_size={page_size}&page={page}'.format(
                page_size=page_size, page=page))
            start = time.time()
            r = requests.get(url)
            end = time.time()
            msg = 'Failed on %s' % url
            self.assertEqual(r.status_code, 200, msg)
            self.assertTrue(end - start < self.timeout, msg)


class DasTestCase(ApiV1BaseClass):
    """
    Tests for DAS endpoints.
    """
    def test_valid_das_annotation_request(self):
        """
        Test DAS `feature` method response.
        """
        target = 'das/RNAcentral_GRCh38/features?segment=Y:25183643,25184773'
        url = self._get_api_url(target)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.upi_with_genomic_coordinates, r.text)
        self._validate_xml(r.text)

    def test_das_request_no_annotation(self):
        """
        Test DAS `feature` method response with no annotations.
        """
        target = 'das/RNAcentral_GRCh38/features?segment=Y:100,120'
        url = self._get_api_url(target)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('FEATURE', r.text)
        self._validate_xml(r.text)

    def test_das_source(self):
        """
        Test DAS `sources` method.
        """
        target = 'das/sources'
        url = self._get_api_url(target)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('RNAcentral_GRCh38', r.text)
        self._validate_xml(r.text)

    def test_das_stylesheet(self):
        """
        Test DAS `stylesheet` method.
        """
        target = 'das/RNAcentral_GRCh38/stylesheet'
        url = self._get_api_url(target)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('exon:non_coding:rnacentral', r.text)
        self._validate_xml(r.text)

    def _validate_xml(self, text):
        """
        Validate xml input.
        """
        try:
            xml.dom.minidom.parseString(text)
        except xml.parsers.expat.ExpatError:
            self.assertEqual(0, 1, "Invalid XML")


class SpeciesSpecificIdsTestCase(ApiV1BaseClass):
    """
    Tests for the species-specific endpoints.
    """
    upi = 'URS000047C79B'
    taxid = 9606

    def test_species_specific_id(self):
        """
        Get an existing upi and taxid.
        """
        url = self._get_api_url('rna/%s/%i' % (self.upi, self.taxid))
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['rnacentral_id'], '%s_%i' % (self.upi, self.taxid))
        self.assertEqual(r.json()['is_active'], True)

    def test_nonexistent_taxid(self):
        """
        Non-existent taxid should return a 404 error.
        """
        taxid = 00000
        url = self._get_api_url('rna/%s/%i' % (self.upi, taxid))
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)

    def test_inactive_entry(self):
        """
        When there are no active xrefs for a taxid,
        the `is_active` field should be `False`.
        """
        upi = 'URS000017C633'
        taxid = 9606
        url = self._get_api_url('rna/%s/%i' % (upi, taxid))
        r = requests.get(url)
        self.assertEqual(r.json()['is_active'], False)


def setup_django_environment():
    """
    Setup Django environment in order for the imports to work.
    """
    os.environ['DJANGO_SETTINGS_MODULE'] = 'rnacentral.settings'
    project_dir = os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)))
    sys.path.append(project_dir)
    django.setup()


def parse_arguments():
    """
    Parse arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    ApiV1BaseClass.base_url = args.base_url

    sys.argv[1:] = args.unittest_args

def run_tests():
    """
    Organize and run the test suites.
    """
    suites = [
        unittest.TestLoader().loadTestsFromTestCase(BasicEndpointsTestCase),
        unittest.TestLoader().loadTestsFromTestCase(SpeciesSpecificIdsTestCase),
        unittest.TestLoader().loadTestsFromTestCase(DasTestCase),
        unittest.TestLoader().loadTestsFromTestCase(RandomEntriesTestCase),
        unittest.TestLoader().loadTestsFromTestCase(FiltersTestCase),
        unittest.TestLoader().loadTestsFromTestCase(OutputFormatsTestCase),
        unittest.TestLoader().loadTestsFromTestCase(NestedXrefsTestCase),
        unittest.TestLoader().loadTestsFromTestCase(RnaEndpointsTestCase),
        unittest.TestLoader().loadTestsFromTestCase(AccessionEndpointsTestCase),
    ]
    unittest.TextTestRunner().run(unittest.TestSuite(suites))


if __name__ == '__main__':
    setup_django_environment()
    from portal.models import Database, Rna
    parse_arguments()
    run_tests()
