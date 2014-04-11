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
Test the ENA sequence search API.

Usage:

# test localhost
python apiv1/search/sequence/tests.py

# test an RNAcentral instance
python apiv1/search/sequence/tests.py --base_url=http://test.rnacentral.org
"""

import requests
import unittest
from rest_client import ENASequenceSearchClient, SequenceSearchError


class ENASequenceSearchTest(unittest.TestCase):
    """
    Tests for the Python ENA REST API client.
    """

    def setUp(self):
        self.client = ENASequenceSearchClient()
        self.sequences = {
            'multiple_hits': 'GATGCCTTGTTGAGCTTTGAAGCACATTGAGAAGAATCTGAAATCCTTCCTCATTATGGGGTGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGACATTCTGGGGTCCCAGTTCAAGTATTTTCCAATGTGAGTCAAGGTGAACCAGAGCCTGAA', # pylint: disable=line-too-long
            'no_hits': 'A'*40,
            'too_short': 'A'*4,
        }

    def tearDown(self):
        pass

    def test_multiple_hits(self):
    	"""
    	Should return an array of dictionaries.
    	"""
        sequence = self.sequences['multiple_hits']
        data = self.client.search(sequence)
        self.assertTrue(len(data) > 0)
        self.assertTrue(isinstance(data[0]['accession'], unicode))
        self.assertTrue(len(data[0]['accession']) > 0)

    def test_no_hits(self):
    	"""
    	Should return an empty array.
    	"""
        sequence = self.sequences['no_hits']
        data = self.client.search(sequence)
        self.assertTrue(len(data) == 0)

    def test_too_short(self):
    	"""
    	Should raise an error.
    	"""
        sequence = self.sequences['too_short']
        with self.assertRaises(SequenceSearchError) as context_manager:
            self.client.submit_query(sequence)
        exc = context_manager.exception
        self.assertEqual(exc.message, 'Invalid sequence')

    def test_get_non_existing_session_id(self):
        """
        Should raise an error.
        """
        job_id = '1234'*6
        jsession_id = 'ABCD'*6
        with self.assertRaises(SequenceSearchError) as context_manager:
            self.client.get_status(job_id, jsession_id)
        exc = context_manager.exception
        self.assertEqual(exc.message, 'Job could not be found')


class RNAcentralSequenceSearchAPITest(unittest.TestCase):
    """
    Tests for the Django sequence search API.
    """
    base_url = ''
    api_url = 'api/v1/sequence-search/'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_api_url(self, extra=''):
        return self.base_url + self.api_url + extra

    def _submit_sequence(self):
        """
        Auxiliary function for submitting a sequence and returning
        job_id and jsession_id.
        """
        sequence = 'GATGCCTTGTTGAGCTTTGAAGCACATTGAGAAGAATCTGAAATCCTTCCTCATTATGGGGTGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGACATTCTGGGGTCCCAGTTCAAGTATTTTCCAATGTGAGTCAAGGTGAACCAGAGCCTGAA' # pylint: disable=line-too-long
        url = self._get_api_url('submit?sequence={0}'.format(sequence))
        return requests.get(url)

    def _check_status(self, job_id, jsession_id):
        """
        """
        url = self._get_api_url('status?job_id={0}&jsession_id={1}'.\
            format(job_id, jsession_id))
        return requests.get(url)

    def test_sequence_submit_success(self):
        r = self._submit_sequence()
        self.assertEqual(r.status_code, 200)
        self.assertTrue('job_id' in r.json())
        self.assertTrue('jsession_id' in r.json())

    def test_sequence_submit_empty(self):
        url = self._get_api_url('submit')
        r = requests.get(url)
        self.assertEqual(r.status_code, 400) # bad request

    def test_sequence_submit_bad_input(self):
        url = self._get_api_url('submit?sequence={0}'.format('A'*4))
        r = requests.get(url)
        self.assertEqual(r.status_code, 500)

    def test_existing_session_id(self):
        # submit a sequence to get job_id and jsession_id
        r = self._submit_sequence()
        data = r.json()
        # check status
        r = self._check_status(data['job_id'], data['jsession_id'])
        data = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertIn(data['status'], ['In progress', 'Done'])
        self.assertNotEqual(data['status'], 'Failed')

    def test_non_existing_session_id(self):
        r = self._check_status('some_job_id', 'some_session_id')
        data = r.json()
        self.assertEqual(r.status_code, 500)
        self.assertEqual(data['status'], 'Failed')
        self.assertEqual(data['message'], 'Job could not be found')


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    RNAcentralSequenceSearchAPITest.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
