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
API v1 tests

The script does not rely on Django in order to avoid
creating test databases and loading initial data.
It can be used to test any RNAcentral web app instance
by specifying the base_url parameter.

Usage:

# test localhost
python apiv1/tests.py

# test an RNAcentral instance
python apiv1/tests.py --base_url http://test.rnacentral.org/
"""

import unittest
import requests
import re


class ApiV1Test(unittest.TestCase):
    """Unit tests entry point"""
    base_url = ''
    api_url = 'api/v1/'

    def setUp(self):
        self.upi = 'URS0000000001'
        self.md5 = '06808191a979cc0b933265d9a9c213fd'
        self.accession = 'Y09527.1:2562..2627:tRNA'
        self.upi_with_genomic_coordinates = 'URS000063A371'

    def tearDown(self):
        pass

    def _get_api_url(self, extra=''):
        return self.base_url + self.api_url + extra

    def test_api_v1_endpoint(self):
        url = self._get_api_url()
        self._check_urls(url)

    def test_rna_endpoint(self):
        url = self._get_api_url('rna')
        self._check_urls(url)

    def test_rna_pagination(self):
        page_size = 5
        url = self._get_api_url('rna/?page=10&page_size=%i' % page_size)
        data = self._check_urls(url)
        self.assertEqual(len(data['results']), page_size)

    def test_rna_sequence(self):
        url = self._get_api_url('rna/%s/' % self.upi)
        data = self._check_urls(url)
        self.assertEqual(data['md5'], self.md5)
        self.assertEqual(data['length'], 66)

    def test_rna_xrefs(self):
        url = self._get_api_url('rna/%s/xrefs' % self.upi)
        self._check_urls(url)

    def test_accession_entry(self):
        url = self._get_api_url('accession/%s' % self.accession)
        self._check_urls(url)

    def test_accession_citations(self):
        url = self._get_api_url('accession/%s/citations' % self.accession)
        self._check_urls(url)

    def test_rna_md5_filter(self):
        url = self._get_api_url('rna/?md5=%s' % self.md5)
        data = self._check_urls(url)
        self.assertEqual(data['results'][0]['rnacentral_id'], self.upi)

    def test_rna_upi_filter(self):
        url = self._get_api_url('rna/?upi=%s' % self.upi)
        data = self._check_urls(url)
        self.assertEqual(data['results'][0]['md5'], self.md5)

    def test_rna_length_filter(self):
        filter_tests = ['rna/?min_length=200000', 'rna/?length=2014',
                        'rna/?max_length=10', 'rna/?min_length=1&max_length=4']
        for filter_test in filter_tests:
            url = self._get_api_url(filter_test)
            data = self._check_urls(url)
            self.assertNotEqual(data['count'], 0)

    def test_rna_database_filter(self):
        for database in ['srpdb', 'mirbase', 'vega', 'tmrna_website']:
            url = self._get_api_url('rna/?database=%s' % database)
            data = self._check_urls(url)
            self.assertNotEqual(data['count'], 0)

    def test_rna_external_id_filter(self):
        filter_tests = ['rna/?external_id=Stap.epid._AF269831', 'rna/?external_id=MIMAT0000091',
                        'rna/?external_id=OTTHUMG00000172092', 'rna/?external_id=Lepto_inter_Lai566']
        for filter_test in filter_tests:
            url = self._get_api_url(filter_test)
            data = self._check_urls(url)
            self.assertNotEqual(data['count'], 0)

    def test_rna_output_formats(self):
        output_formats = ['json', 'yaml', 'api']
        for output_format in output_formats:
            url = self._get_api_url('rna/%s/?format=%s' % (self.upi, output_format))
            r = requests.get(url)
            self.assertEqual(r.status_code, 200)

    def test_hyperlinked_vs_nested_responses(self):
        # hyperlinked
        url = self._get_api_url('rna/')
        data = self._check_urls(url)
        self.assertIn('http', data['results'][0]['xrefs'])
        # flat
        url = self._get_api_url('rna/%s%s' % (self.upi, '?flat=true'))
        data = self._check_urls(url)
        self.assertNotEqual(len(data['xrefs']), 0)

    def test_non_fasta_output_formats(self):
        formats = {'json': 'application/json',
                   'yaml': 'application/yaml',
                   'api': 'text/html'}
        targets = ('rna', 'rna/%s' % self.upi, 'rna/%s/xrefs' % self.upi,
                   'accession/%s' % self.accession, 'accession/%s/citations' % self.accession)
        self._output_format_tester(formats, targets)

    def test_fasta_output(self):
        formats = {'fasta': 'text/fasta'}
        targets = ('rna', 'rna/%s' % self.upi)
        self._output_format_tester(formats, targets)

    def test_gff_output(self):
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
        formats = {'gff3': 'text/gff3'}
        targets = ('rna/%s' % self.upi_with_genomic_coordinates,)
        # test response status codes
        self._output_format_tester(formats, targets)
        # further check the gff text output
        r = requests.get(self._get_api_url(targets[0]+'.gff3'))
        self.assertIn('SO:0000198', r.text)
        # test a sequence without genomic coordinates
        r = requests.get(self._get_api_url('rna/%s.gff3' % self.upi))
        self.assertIn('# Genomic coordinates not available', r.text)

    def test_bed_output(self):
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

    def test_genome_annotations(self):
        targets = ['feature/region/human/Y:26,631,479-26,632,610', 'feature/region/human/2:39,745,816-39,826,679']
        for target in targets:
            url = self._get_api_url(target)
            data = self._check_urls(url)
            self.assertNotEqual(len(data), 0)
            for annotation in data:
                if annotation['feature_type'] == 'transcript':
                    self.assertIn('URS', annotation['external_name'])
                elif annotation['feature_type'] == 'exon':
                    self.assertIn('URS', annotation['Parent'])
                else:
                    self.assertEqual(0, 1, "Unknown genomic annotation type")

    def _output_format_tester(self, formats, targets):
        """
        Auxiliary function for testing output formats.
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

    def _check_urls(self, url):
        """
        Auxiliary function for testing the API with and without trailing slash.
        """
        # remove the trailing slash if present
        if url[-1] == '/':
            url = url[:-1]
        # test without the slash
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        # add the slash back if there are no url parameters
        if '?' not in url:
            url += '/'
            r = requests.get(url)
            self.assertEqual(r.status_code, 200)
        return r.json()


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    ApiV1Test.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
