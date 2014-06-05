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

# add Django project to the path in order to import models in rest_client.py
import os, sys
from os.path import dirname
sys.path.append(os.path.abspath(__file__ + "/../../../.."))
os.environ["DJANGO_SETTINGS_MODULE"] = "rnacentral.settings"

import json
import requests
import time
import unittest
from rest_client import ENASequenceSearchClient, SequenceSearchError, \
                        InvalidSequenceError, StatusNotFoundError


class ENASequenceSearchTest(unittest.TestCase):
    """
    Tests for the Python ENA REST API client.
    """

    def setUp(self):
        self.client = ENASequenceSearchClient()

    def __verify_results(self, test_case):
        """
        Verify that a predefined accession is present in the response text.
        """
        # check whether the ENA accession is returned
        data = self.client.search(test_case['sequence'], map_ids=False)
        self.assertTrue(test_case['accession'] in json.dumps(data))
        # check whether the RNAcentral ids are mapped correctly
        data = self.client.search(test_case['sequence'], map_ids=True)
        self.assertTrue(test_case['upi'] in json.dumps(data))

    def test_find_itself_rfam_sequence(self):
        """
        To test that RFAM product is searched correctly.
        """
        test_case = {
            'sequence': 'AACTACATTATCGATGTATAGATTCACCCGCGAGATGATGTGGCTGTTTCACCTAGGACGAGGACATGGCATCCTATTACCAGCCATCGCACGAAATTAATATGATGCCACGTCCTCATACTAGATGAAACAACCACGTCGTCATATCACAAGTGAATCCATTCATCGATAGTGTGGTT', # pylint: disable=line-too-long
            'accession': 'AAAA02000007.1:34766..34944:rfam',
            'upi': 'URS000063CC7F',
        }
        self.__verify_results(test_case)

    def test_find_itself_minimum_length(self):
        """
        20 nucleotides, minimum length
        """
        test_case = {
            'sequence': 'ACCAGUGUUCAGACGGUGGA',
            'accession': 'DQ930848.1:1..20:misc_RNA',
            'upi': 'URS00003989D1',
        }
        self.__verify_results(test_case)

    def test_find_itself_interface_example_1(self):
        """
        This sequence is used as an example in the user interface.
        """
        test_case = {
            'sequence': 'UGAGGUAGUAGAUUGUAUAGUU',
            'accession': 'HAAO01000006.1:1..22:ncRNA',
            'upi': 'URS00003B7674',
        }
        self.__verify_results(test_case)

    def test_find_itself_interface_example_2(self):
        """
        This sequence is used as an example in the user interface.
        """
        test_case = {
            'sequence': 'UGCCUGGCGGCCGUAGCGCGGUGGUCCCACCUGACCCCAUGCCGAACUCAGAAGUGAAACGCCGUAGCGCCGAUGGUAGUGUGGGGUCUCCCCAUGCGAGAGUAGGGAACUGCCAGGCAU',
            'accession': 'CU928163.2:4660940..4661059:rRNA',
            'upi': 'URS0000049E57',
        }
        self.__verify_results(test_case)

    def test_find_itself_long_sequence(self):
        """
        4000 nucleotides long.
        """
        test_case = {
            'sequence': 'GGGGUCUCGGGUCACGUGACAGGCGGCCCAAUCGCACUCGCGCGACGGAAAGCGCCACGGACGUCGGAGGCCCAGGGGGCGGGGCUCCCGAGCUCCGCUCUUUCGUGGUCGGGCGGCGGACCGCACUGUAUUUUUUCCUUCCGGGGGCGGCGGAGCCCAGGGCUAUCCCGGCCUCCGCUCAUACCCGGAGGGCCGGCAGGCGUUCAGUCCUCCAGCCGGUGAGGCUCGGGCCGGGGUGUCGGGACCGCCUGAACACGCGGGCUCUGGGAGCUUCAGGGACCAGGGAGCCACCUCGGCCGAGUUGCGUCGCAGACUACAGCUCCCAGCAUGCGCCGCCGCUCCCAGCAUGCACCUUCCUCCCGAAACGCGUCUCUGCUUCCGGCGCUCUGCUGCGGAGGCCGUGGCCGCGGGUAGUUGGGAGGAACCGAGAUUUACGCUUGGUAAGGCAAGUUGCGAGCUGUCCGGCGCCGGUCGAGUUCCUGCCGCCGUCGUCGUCAGGCAGGGGAGAAGGGGGCCUCAACCCCUCUAGUGACAGCUGUUUGCUACCUAAUAGGGCUUUUCAUCCCACCGGGCCCCAGGGCCUUCGUUAGGAGCCCAGCAGGCUCAACUUCUUGCUGUGGUUCUGGAAAAGGGAGUGACCACCUGGCUCAACACCUCUCUCUGUGAUGUGUUUGGGAGUUUUGGGAAAUGAGACGGCUCCGAGGGAAGAGCUUGAGGGAGCGGCGUCGCACUCGUUCGACCUUCCCGGGCCUGGGCUUUGUUUCUAGGCAUUUUAGGUUGAACGCUCUACAUCUUAACUGGGGGCAGGGGAGGUGGCCAGAGCAUCCCGCUGAGCGUUUUCCGAUUCCCCAGAUGGCCAGGCACCUGGUCCUGGUGGCUGGACAGUGACCCCGUGGACGCACAUUUACAGCUAUAGCCAUUCAGUGCCGCGGGGAGGUGAGGAUAGUGAUCCUGGGACCUGCUCGAGGAUUCACCCUUGCCCCAAGAACCUGUUCCAUUCCCAGGAAUGAAGGCGGUCAGGCAGGGGAGGAGAAGGGGGCCUCAACUCUUCUAGUGACAGCAGUUUGCCACCUAAUAGAGCUUUUCAGAUUUUGCCUCCUCAGGCCAUUUUACUCAGCCUCGGACUAUCAAGGAUGGUCACAUUGAAGCUGUUUUUCUGCAGUCAGGAGCGAAAAGUCCCGGCUGUUGAAGGAGAAACUGAAUCUGGUUCAGGAGUCCCAGGUUCCUCCCUCUGAGAGGCCAGGUGGGGCCUGCGUGAGUAGCAGUUGUUCAGGUGGCAGGACACUGCUGUUUUCAUCCCACCUGGCCCCAGGCCCCUGAUUAGGGGCCCAGAGUGCUUAUGUACUUGCCUCGGUCUGAGAAAGGGAGUGACUGCAUAGCCCAACACCUGUGGGAUGCCUCACUGCCCAGAUGUUUCAUCUCCGGGAUGCUUCAUUGCCCAUUCAGCACCCUCUAUGGUGCUGACUCUUCCGGAAGAUGUUUCUGAUUCCUUGCUAGGCUGGUGGUUGCACCAUAGCUGAGAGGACUCAAGAAGAGCCUGGUCUCAGCUUCACCUAGGAGUCCCGGAGGAGUAAGAAACACGUAUCUUUCCUGUUCUGGGCACAUAUGGGUGGGUAGCAGAGCUGAGGCUAGCUGAGGAUCCCGACUCUCCUUUGGGAGCCUUUGUUGUGCCGCUCUCCCAGGCUGAUCAGAUCUGGAGAGCUAACAGCUUCCUGUGGCCACAUCUGUGUCCAAGGCUGGGCCCAUGCCUGUAGCCAGAUUGCCAGGAUCUGGAAGGGGCCAAGAGACAGCUGGUGCUGGGUAGGCAGCAGCCCUGUGUCAACCUGCCCCCACUAUUACCCCAUGCUGUGAUUUGCAUGUGGUCUGCCCCUGCCCAAAAUGGUAUUGAAAUUUGAGCCUCAAUGAGGCAGUGUUAGGAGGUGGUGCCUAGUAGGAGGAGUUUGGGUAAUAGGGGUGGAUCCCUCAUGGAUAGGUUAGUGUCCUUUGUGGAGGGGUGAGUUCCCAUGAGAGCUGGUUAGAGAGUCAGCCUUCCUGCGGUUGUCUCUUGCUUCCUCUCUCGCCAUAUGGCCACGUAAUCUCUUUGUGCAUGCCUCUCCCCUUCUACUUGCUGCCUUGAGUUGAAGUAGCAUGAGGCCCUCACCAGGUGCAGCUGCCCAAUCUUGAAAUUUCCACCAGAAUUUUGAGCCAAAUAAACCUGUUUUGCUUUUUUAAAAAAAUAAAUUCCCCCACCUUGGCUGGGCGCAGUGGCUCACGCCUGUAAUCCCAGCACUUUGGGAGGCCGAGGCGGGCGGAUCACGAGGUCAGAUCGAGACCAUCUUGGCUAACACGGUGAAACCCCAUCUCUACUGAAAAAAAAAAAGAAACAAAAAAAUUAGCCAGGUGUGGUGGCGGGCACCUGUAGUCCCAGCCCCUCACUCGGGAGGCUGAUUGAGGCAGGAGAAUGGUGUGAACCCGGGAGGCGGAGCUUGCAGUGAGCCCAGAUCGCACCACUGCACUCCAGCCUGGGCGACAGAGCGAGACUCCGUCUCUAAAUAAAUAAAUAAAUAAAUAAAACAAACCCAACCUCAGGUAUAGCAGUGUGAAACAGACUAAGACAUUCCACAUGCCCUGUGGUCCCAUCUGCUACCCCAGGGUGCAAAGAUGUUCCCUCAGCCCUGAAGAAUGACAUUCCCCCCGGCUCCUGGGAUAUCUGGAGGGGUUGUAAGCAGCUUGGGUUGGUGAGAUAAGGAGUUUGGGGGGCAGCUGAUUCAUGACCCUGGCCUCCUCAACUGCAGGCUCUUGGUCUGAAGUACUGUAAUUAAAGUAUGAGAGCCUCGGGGCCCUCACUUCAAGGAGGGAAGAGCAUCCCCAUGCCUCAGCGUUUGGGGAUUGUAGGGAGAUGAGAGUCCUUCAGGUGGGACUAGUUCCCGCCAUGACCCCACUGCUGGCCAGUGGCCUGAAACGCAUCUGACCACUUCUCAGGUUCAUGGGUGUUGAGGAGGAGCCCUGUGGAAUCAACCCUGUCUGCCUCCUCUUAUCCUGCCACUCCUCUUGCUCUGUCUGGAUGACUGCCCUUGUUUUUCAAGGGAAUGUUCCCUGUCUUCCUCAGCCAGGAUUUUUUCUGAACUUGACAUCUCCGUUUGUUCAGGGGGCAAUCAUUGGGCACUUCACUGUGCUGGUCCUUGCAUUCUCAUGGAGAUGCAGAGAUUAAAAAUUAGUAUCUUGUCCACAUACUGCCCAGAGUUAGCAAGGAUUGCUUUUCUGUGGAUUUGUCUCAGGUCGGGCACAGUGGGGGUAGGGUCCUUCUCGAACCUUUUCCUAGCCUAAAGGUUCCAGCUGAAUCUUCCCAGGCAGGGCUGAAACAGGAACCAUUUUAGGCUUUGCUGCAACCCAUGGUCAGUUCUCCAAGAAAAGUGAAGAGGGUUCCACCUGGGGCAGCCCUCAAGGGCUCAGAGGGCCAAAACACACGUACAACAUGUUGAGACACUGAGUUUGUGCGAUCCCCACACAUCUCAGCAGUGAGUAUUUCUGCCUCAUUUUACCGAUGAGGAACCUGAGCUUCAAAGGGAAGAGGUGACAGCUCAGGACCACACAGCUGUAGGUAGGAGGCAGGAAAAUAGGGUCUGAGUGCAGGGAACAUAGGCUGAUUCACACUUCAGUUAUGAUAGGAAAUACCUUCUCCAUAGGACAUAGGCCAAGCAAAUGACUUUGUAACUUCAUCCUCUCCAUCUGCAUAACGUGUGCCCCAAGUAACCAAUGGAAUCACCUAGAGGGUGUUUAAACUCUCAGAAGUUCUGUAACAGGCUCUCCAUCUACAUAACGUGUGCCCCAAGUAACCAAUGGAAUCACCUAGAGGGUAUUUAAACUCUCUGAAGUUCUGUAACAGGGCUUUUGUGCUCCUAUGCUCAGGCUCACCCCCACACUGUGGAGUGUACUUUCAUUUUCAAUAAAUCCCUUCAUUCCUUCUUUGCUCUCUGUGUGUGUUUUGUCCAAUUCUUUAUUUAAGACGCCAAGAACCUGG',  # pylint: disable=line-too-long
            'accession': 'HG495355.1:1..4000:ncRNA',
            'upi': 'URS000016DD3F',
        }
        self.__verify_results(test_case)

    def test_too_short(self):
        """
        Should raise an error.
        """
        sequence = 'A'*4
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
        with self.assertRaises(StatusNotFoundError) as context_manager:
            self.client.get_status(job_id, jsession_id)
        exc = context_manager.exception


class RNAcentralAPITestBaseClass(unittest.TestCase):
    """
    Base class for Django sequence search API tests.
    """
    base_url = ''
    api_url = 'api/v1/sequence-search/'
    # URS00000B15DA
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
        self.assertTrue('url' in r.json())

    def test_sequence_submit_empty(self):
        url = self._get_api_url('submit')
        r = requests.get(url)
        self.assertEqual(r.status_code, 400) # bad request

    def test_sequence_submit_bad_input(self):
        short_sequence = 'A'*4
        url = self._get_api_url('submit?sequence={0}'.format(short_sequence))
        r = requests.get(url)
        self.assertEqual(r.status_code, 400) # bad request


class StatusAPITest(RNAcentralAPITestBaseClass):
    """
    Tests for search status retrieval.
    """

    def test_existing_session_id(self):
        # submit a sequence to get job_id and jsession_id
        r = self._submit_sequence(self.sequence)
        # check status
        r = requests.get(r.json()['url'])
        data = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertTrue('url' in data)
        self.assertIn(data['status'], ['In progress', 'Done'])
        self.assertNotEqual(data['status'], 'Failed')

    def test_non_existing_session_id(self):
        url = self._get_api_url('status?job_id={0}&jsession_id={1}'.format(
                                'some_job_id', 'some_session_id'))
        r = requests.get(url)
        data = r.json()
        self.assertEqual(r.status_code, 404)
        self.assertEqual(data['status'], 'Failed')


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
