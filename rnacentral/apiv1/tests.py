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
        pass

    def tearDown(self):
        pass

    def _get_api_url(self, extra=''):
        return self.base_url + self.api_url + extra

    def test_api_v1_endpoint(self):
        url = self._get_api_url()
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

    def test_rna_endpoint(self):
        url = self._get_api_url('rna/')
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

    def test_rna_pagination(self):
        url = self._get_api_url('rna/?page=10&page_size=5')
        r = requests.get(url)
        data = r.json()
        self.assertEqual(len(data['results']), 5)

    def test_rna_sequence(self):
        url = self._get_api_url('rna/UPI0000000001/')
        r = requests.get(url)
        data = r.json()
        self.assertEqual(data['md5'], '06808191a979cc0b933265d9a9c213fd')
        self.assertEqual(data['length'], 66)

    def test_rna_xrefs(self):
        url = self._get_api_url('rna/UPI0000000001/xrefs')
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

    def test_accession_endpoint(self):
        url = self._get_api_url('accession/')
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

    def test_accession_citations(self):
        url = self._get_api_url('accession/Y09527.1:2562..2627:tRNA/citations/')
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

    def test_md5_lookup(self):
        url = self._get_api_url('rna/?md5=06808191a979cc0b933265d9a9c213fd')
        r = requests.get(url)
        data = r.json()
        self.assertEqual(data['results'][0]['upi'], 'UPI0000000001')


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
