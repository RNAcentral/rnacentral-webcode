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
import time
import unittest
from rest_client import ENASequenceSearchClient, SequenceSearchError, \
                        InvalidSequenceError


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
        with self.assertRaises(InvalidSequenceError) as context_manager:
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


class RNAcentralAPITestBaseClass(unittest.TestCase):
    """
    Base class for Django sequence search API tests.
    """
    base_url = ''
    api_url = 'api/v1/sequence-search/'
    # URS000063A371
    sequence = 'GATGCCTTGTTGAGCTTTGAAGCACATTGAGAAGAATCTGAAATCCTTCCTCATTATGGGGTGTGTTCAGGCTGCTGAGGTGCCCATTCTCAAGATTTTCACTGGACATTCTGGGGTCCCAGTTCAAGTATTTTCCAATGTGAGTCAAGGTGAACCAGAGCCTGAA' # pylint: disable=line-too-long

    def _get_api_url(self, extra=''):
        return self.base_url + self.api_url + extra

    def _submit_sequence(self, sequence):
        """
        Auxiliary function for submitting a sequence and returning
        job_id and jsession_id.
        """
        url = self._get_api_url('submit?sequence={0}'.format(sequence))
        return requests.get(url)


class SubmitAPITest(RNAcentralAPITestBaseClass):
    """
    Tests for submitting a sequence.
    """

    def test_sequence_submit_success(self):
        r = self._submit_sequence(self.sequence)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('job_id' in r.json())
        self.assertTrue('jsession_id' in r.json())

    def test_sequence_submit_empty(self):
        url = self._get_api_url('submit')
        r = requests.get(url)
        self.assertEqual(r.status_code, 400) # bad request

    def test_sequence_submit_bad_input(self):
        short_sequence = 'A'*4
        url = self._get_api_url('submit?sequence={0}'.format(short_sequence))
        r = requests.get(url)
        self.assertEqual(r.status_code, 500)


class StatusAPITest(RNAcentralAPITestBaseClass):
    """
    Tests for search status retrieval.
    """

    def _check_status(self, job_id, jsession_id):
        """
        """
        url = self._get_api_url('status?job_id={0}&jsession_id={1}'.\
            format(job_id, jsession_id))
        return requests.get(url)

    def test_existing_session_id(self):
        # submit a sequence to get job_id and jsession_id
        r = self._submit_sequence(self.sequence)
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


class ResultsAPITest(RNAcentralAPITestBaseClass):
    """
    Tests for search results retrieval.
    """

    def test_results_bad_request(self):
        url = self._get_api_url('results')
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_results_not_available(self):
        fake_id = 'ABCD'*6
        job_id = jsession_id = fake_id
        url = self._get_api_url('results?job_id={0}&jsession_id={1}'.format(
                                job_id, jsession_id))
        r = requests.get(url)
        self.assertEqual(r.json()['results'], [])
        self.assertEqual(r.status_code, 404)

    def test_results_pagination(self):
        PAGE_SIZE = 10

        # submit a test sequence and wait for results
        r = self._submit_sequence('GGGGCCGAAACAGGAUCGACGAACGUCUAAAGGGGUUAGCUUUGUCUCGGCUGGGUGCCACCGUUAUCGGCCUAAAUUGUACAGUUGCAAACGACAACCGUGCUCCGGUGGCCGUUGCUGCGUAAGCAGUAACAACACCGAAACUUAAGUCCUUGCGCCUAGCAGCGUAAGGCGGGGUUCGCAGGCACCUGGCAACAGAAGCCUGCACA')
        jsession_id = r.json()['jsession_id']
        job_id = r.json()['job_id']
        time.sleep(5)

        # default page and page_size
        url = self._get_api_url('results?job_id={0}&'
                                'jsession_id={1}'.format(job_id, jsession_id))
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()['results']), PAGE_SIZE)

        # page=1
        page = 1
        url = self._get_api_url('results?job_id={0}&jsession_id={1}&'
                                'page={2}'.format(job_id, jsession_id, page))
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        data1 = r.json()['results']
        self.assertEqual(len(data1), PAGE_SIZE)

        # page=2
        page = 2
        url = self._get_api_url('results?job_id={0}&jsession_id={1}&'
                                'page={2}'.format(job_id, jsession_id, page))
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        data2 = r.json()['results']
        self.assertEqual(len(data2), PAGE_SIZE)
        self.assertNotEqual(data1, data2)

        # page=1&page_size=20
        page = 1
        page_size = 20
        url = self._get_api_url('results?job_id={0}&jsession_id={1}&'
                                'page={2}&page_size={3}'.format(job_id,
                                jsession_id, page, page_size))
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()['results']), page_size)

        # TODO: test pagination over non-existing ranges
        # page=10000000
        # page = pow(10, 7)
        # url = self._get_api_url('results?job_id={0}&jsession_id={1}&'
        #                         'page={2}'.format(job_id, jsession_id, page))
        # r = requests.get(url)
        # print url
        # self.assertEqual(r.status_code, 404)
        # self.assertEqual(len(r.json()['results']), 0)

        # # page=1&page_size=10000000
        # page = 1
        # page_size = pow(10, 7)
        # url = self._get_api_url('results?job_id={0}&jsession_id={1}&'
        #                         'page={2}&page_size={3}'.format(job_id,
        #                         jsession_id, page, page_size))
        # r = requests.get(url)
        # self.assertEqual(r.status_code, 404)
        # self.assertEqual(len(r.json()['results']), 0)


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000/')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] != '/':
        args.base_url += '/'
    RNAcentralAPITestBaseClass.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
