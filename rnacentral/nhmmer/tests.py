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
Usage:

# test localhost
python tests.py

# test an RNAcentral instance
python tests.py --base_url http://test.rnacentral.org/
"""

import argparse
import django
import json
import os
import requests
import sys
import time
import unittest

from random import randint
from django.core.urlresolvers import reverse

from messages import messages
from settings import MAX_LENGTH


class NhmmerTestCase(unittest.TestCase):
    """
    Base class for export search results testing.
    """
    base_url = ''

    def _submit_query(self, query, method='get'):
        """
        Submit a query and return the response object.
        """
        url = self.base_url + reverse('nhmmer-submit-job')
        if method == 'get':
            url += '?q=%s' % query
            return requests.get(url)
        elif method == 'post':
            return requests.post(url, data={'q': query})

    def _get_results(self, sequence):
        """
        Submit query, wait until the job is finished,
        return the results.
        """
        if len(sequence) > 1000:
            method = 'post'
        else:
            method = 'get'
        r = self._submit_query(query=sequence, method=method)
        status_url = r.json()['url']
        while True:
            r = requests.get(status_url)
            data = r.json()
            status = data['status']
            if status == 'finished':
                break
            elif status == 'failed':
                self.assertTrue(False, 'Job failed')
            time.sleep(1)
        results_url = data['url']
        r = requests.get(results_url)
        return r

    def _check_results(self, query):
        """
        Get search results and run some basic tests.
        """
        r = self._get_results(query['sequence'])
        self.assertEqual(r.status_code, 200, 'Failed on %s' % query['id'])
        self.assertTrue(r.json()['count'] > 0, 'Failed on %s' % query['id'])
        self.assertEqual(r.json()['results'][0]['rnacentral_id'], query['id'])


class SubmitTests(NhmmerTestCase):
    """
    Tests for the job submission endpoint.
    """
    msg_type = 'submit'

    def test_empty_query(self):
        """
        Test empty query.
        """
        sequence = ''
        status = 400
        message = messages[self.msg_type][status]['no_sequence']['message']
        r = self._submit_query(query=sequence)
        self.assertEqual(r.status_code, status)
        self.assertEqual(r.json()['message'], message)

    def test_too_short_sequence(self):
        """
        Test short query sequence.
        """
        sequence = 'ACGU'
        status = 400
        message = messages[self.msg_type][status]['too_short']['message']
        r = self._submit_query(query=sequence)
        self.assertEqual(r.status_code, status)
        self.assertEqual(r.json()['message'], message)

    def test_too_long_sequence(self):
        """
        Test long query sequence.
        """
        sequence = 'A' * (MAX_LENGTH + 1)
        status = 400
        message = messages[self.msg_type][status]['too_long']['message']
        r = self._submit_query(query=sequence, method='post')
        self.assertEqual(r.status_code, status)
        self.assertEqual(r.json()['message'], message)

    def test_get_method(self):
        """
        Test query submission using GET.
        """
        sequence = 'ACGU' * 20
        status = 201
        r = self._submit_query(query=sequence)
        self.assertEqual(r.status_code, status)
        self.assertTrue('id' in r.json())

    def test_post_method(self):
        """
        Test query submission using POST.
        """
        sequence = 'ACGU' * 20
        status = 201
        r = self._submit_query(query=sequence, method='post')
        self.assertEqual(r.status_code, status)
        self.assertTrue('id' in r.json())


class GetStatusTests(NhmmerTestCase):
    """
    Tests for the job status endpoint.
    """
    msg_type = 'status'

    def test_no_job_id(self):
        """
        No job id is provided in the url.
        """
        url = self.base_url + reverse('nhmmer-job-status')
        status = 400
        message = messages[self.msg_type][status]['message']
        r = requests.get(url)
        self.assertEqual(r.status_code, status)
        self.assertEqual(r.json()['message'], message)

    def test_invalid_job_id(self):
        """
        Invalid job id or job id not found.
        """
        job_id = 'foobar'
        url = self.base_url + reverse('nhmmer-job-status') + '?id=%s' % job_id
        status = 404
        message = messages[self.msg_type][status]['message']
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()['message'], message)

    def test_valid_job(self):
        """
        Submit a small query and check its status.
        """
        sequence = 'ACGU' * 20
        status = 200
        # submit query
        r = self._submit_query(query=sequence)
        # check query status
        r = requests.get(r.json()['url'])
        self.assertEqual(r.status_code, 200)
        self.assertTrue('status' in r.json())


class ResultsTests(NhmmerTestCase):
    """
    Tests for the results endpoint.
    """
    def test_URS0000000001(self):
        """
        Test the first RNAcentral id.
        """
        query = {
            'id': 'URS0000000001',
            'sequence': 'AUUGAACGCUGGCGGCAGGCCUAACACAUGCAAGUCGAGCGGUAGAGAGAAGCUUGCUUCUCUUGAGAGCGGCGGACGGGUGAGUAAUGCCUAGGAAUCUGCCUGGUAGUGGGGGAUAACGCUCGGAAACGGACGCUAAUACCGCAUACGUCCUACGGGAGAAAGCAGGGGACCUUCGGGCCUUGCGCUAUCAGAUGAGC',  # pylint: disable=line-too-long
        }
        self._check_results(query)

    def test_minimum_length(self):
        """
        20 nucleotides, minimum length
        """
        query = {
            'id': 'URS00003989D1',
            'sequence': 'ACCAGUGUUCAGACGGUGGA',
        }
        self._check_results(query)

    def test_interface_example_1(self):
        """
        This sequence is used as an example in the user interface.
        """
        query = {
            'id': 'URS00003B7674',
            'sequence': 'UGAGGUAGUAGAUUGUAUAGUU',
        }
        self._check_results(query)

    def test_interface_example_2(self):
        """
        This sequence is used as an example in the user interface.
        """
        query = {
            'id': 'URS0000049E57',
            'sequence': 'UGCCUGGCGGCCGUAGCGCGGUGGUCCCACCUGACCCCAUGCCGAACUCAGAAGUGAAACGCCGUAGCGCCGAUGGUAGUGUGGGGUCUCCCCAUGCGAGAGUAGGGAACUGCCAGGCAU',
        }
        self._check_results(query)

    def test_long_sequence(self):
        """
        4000 nucleotides long.
        """
        query = {
            'id': 'URS000016DD3F',
            'sequence': 'GGGGUCUCGGGUCACGUGACAGGCGGCCCAAUCGCACUCGCGCGACGGAAAGCGCCACGGACGUCGGAGGCCCAGGGGGCGGGGCUCCCGAGCUCCGCUCUUUCGUGGUCGGGCGGCGGACCGCACUGUAUUUUUUCCUUCCGGGGGCGGCGGAGCCCAGGGCUAUCCCGGCCUCCGCUCAUACCCGGAGGGCCGGCAGGCGUUCAGUCCUCCAGCCGGUGAGGCUCGGGCCGGGGUGUCGGGACCGCCUGAACACGCGGGCUCUGGGAGCUUCAGGGACCAGGGAGCCACCUCGGCCGAGUUGCGUCGCAGACUACAGCUCCCAGCAUGCGCCGCCGCUCCCAGCAUGCACCUUCCUCCCGAAACGCGUCUCUGCUUCCGGCGCUCUGCUGCGGAGGCCGUGGCCGCGGGUAGUUGGGAGGAACCGAGAUUUACGCUUGGUAAGGCAAGUUGCGAGCUGUCCGGCGCCGGUCGAGUUCCUGCCGCCGUCGUCGUCAGGCAGGGGAGAAGGGGGCCUCAACCCCUCUAGUGACAGCUGUUUGCUACCUAAUAGGGCUUUUCAUCCCACCGGGCCCCAGGGCCUUCGUUAGGAGCCCAGCAGGCUCAACUUCUUGCUGUGGUUCUGGAAAAGGGAGUGACCACCUGGCUCAACACCUCUCUCUGUGAUGUGUUUGGGAGUUUUGGGAAAUGAGACGGCUCCGAGGGAAGAGCUUGAGGGAGCGGCGUCGCACUCGUUCGACCUUCCCGGGCCUGGGCUUUGUUUCUAGGCAUUUUAGGUUGAACGCUCUACAUCUUAACUGGGGGCAGGGGAGGUGGCCAGAGCAUCCCGCUGAGCGUUUUCCGAUUCCCCAGAUGGCCAGGCACCUGGUCCUGGUGGCUGGACAGUGACCCCGUGGACGCACAUUUACAGCUAUAGCCAUUCAGUGCCGCGGGGAGGUGAGGAUAGUGAUCCUGGGACCUGCUCGAGGAUUCACCCUUGCCCCAAGAACCUGUUCCAUUCCCAGGAAUGAAGGCGGUCAGGCAGGGGAGGAGAAGGGGGCCUCAACUCUUCUAGUGACAGCAGUUUGCCACCUAAUAGAGCUUUUCAGAUUUUGCCUCCUCAGGCCAUUUUACUCAGCCUCGGACUAUCAAGGAUGGUCACAUUGAAGCUGUUUUUCUGCAGUCAGGAGCGAAAAGUCCCGGCUGUUGAAGGAGAAACUGAAUCUGGUUCAGGAGUCCCAGGUUCCUCCCUCUGAGAGGCCAGGUGGGGCCUGCGUGAGUAGCAGUUGUUCAGGUGGCAGGACACUGCUGUUUUCAUCCCACCUGGCCCCAGGCCCCUGAUUAGGGGCCCAGAGUGCUUAUGUACUUGCCUCGGUCUGAGAAAGGGAGUGACUGCAUAGCCCAACACCUGUGGGAUGCCUCACUGCCCAGAUGUUUCAUCUCCGGGAUGCUUCAUUGCCCAUUCAGCACCCUCUAUGGUGCUGACUCUUCCGGAAGAUGUUUCUGAUUCCUUGCUAGGCUGGUGGUUGCACCAUAGCUGAGAGGACUCAAGAAGAGCCUGGUCUCAGCUUCACCUAGGAGUCCCGGAGGAGUAAGAAACACGUAUCUUUCCUGUUCUGGGCACAUAUGGGUGGGUAGCAGAGCUGAGGCUAGCUGAGGAUCCCGACUCUCCUUUGGGAGCCUUUGUUGUGCCGCUCUCCCAGGCUGAUCAGAUCUGGAGAGCUAACAGCUUCCUGUGGCCACAUCUGUGUCCAAGGCUGGGCCCAUGCCUGUAGCCAGAUUGCCAGGAUCUGGAAGGGGCCAAGAGACAGCUGGUGCUGGGUAGGCAGCAGCCCUGUGUCAACCUGCCCCCACUAUUACCCCAUGCUGUGAUUUGCAUGUGGUCUGCCCCUGCCCAAAAUGGUAUUGAAAUUUGAGCCUCAAUGAGGCAGUGUUAGGAGGUGGUGCCUAGUAGGAGGAGUUUGGGUAAUAGGGGUGGAUCCCUCAUGGAUAGGUUAGUGUCCUUUGUGGAGGGGUGAGUUCCCAUGAGAGCUGGUUAGAGAGUCAGCCUUCCUGCGGUUGUCUCUUGCUUCCUCUCUCGCCAUAUGGCCACGUAAUCUCUUUGUGCAUGCCUCUCCCCUUCUACUUGCUGCCUUGAGUUGAAGUAGCAUGAGGCCCUCACCAGGUGCAGCUGCCCAAUCUUGAAAUUUCCACCAGAAUUUUGAGCCAAAUAAACCUGUUUUGCUUUUUUAAAAAAAUAAAUUCCCCCACCUUGGCUGGGCGCAGUGGCUCACGCCUGUAAUCCCAGCACUUUGGGAGGCCGAGGCGGGCGGAUCACGAGGUCAGAUCGAGACCAUCUUGGCUAACACGGUGAAACCCCAUCUCUACUGAAAAAAAAAAAGAAACAAAAAAAUUAGCCAGGUGUGGUGGCGGGCACCUGUAGUCCCAGCCCCUCACUCGGGAGGCUGAUUGAGGCAGGAGAAUGGUGUGAACCCGGGAGGCGGAGCUUGCAGUGAGCCCAGAUCGCACCACUGCACUCCAGCCUGGGCGACAGAGCGAGACUCCGUCUCUAAAUAAAUAAAUAAAUAAAUAAAACAAACCCAACCUCAGGUAUAGCAGUGUGAAACAGACUAAGACAUUCCACAUGCCCUGUGGUCCCAUCUGCUACCCCAGGGUGCAAAGAUGUUCCCUCAGCCCUGAAGAAUGACAUUCCCCCCGGCUCCUGGGAUAUCUGGAGGGGUUGUAAGCAGCUUGGGUUGGUGAGAUAAGGAGUUUGGGGGGCAGCUGAUUCAUGACCCUGGCCUCCUCAACUGCAGGCUCUUGGUCUGAAGUACUGUAAUUAAAGUAUGAGAGCCUCGGGGCCCUCACUUCAAGGAGGGAAGAGCAUCCCCAUGCCUCAGCGUUUGGGGAUUGUAGGGAGAUGAGAGUCCUUCAGGUGGGACUAGUUCCCGCCAUGACCCCACUGCUGGCCAGUGGCCUGAAACGCAUCUGACCACUUCUCAGGUUCAUGGGUGUUGAGGAGGAGCCCUGUGGAAUCAACCCUGUCUGCCUCCUCUUAUCCUGCCACUCCUCUUGCUCUGUCUGGAUGACUGCCCUUGUUUUUCAAGGGAAUGUUCCCUGUCUUCCUCAGCCAGGAUUUUUUCUGAACUUGACAUCUCCGUUUGUUCAGGGGGCAAUCAUUGGGCACUUCACUGUGCUGGUCCUUGCAUUCUCAUGGAGAUGCAGAGAUUAAAAAUUAGUAUCUUGUCCACAUACUGCCCAGAGUUAGCAAGGAUUGCUUUUCUGUGGAUUUGUCUCAGGUCGGGCACAGUGGGGGUAGGGUCCUUCUCGAACCUUUUCCUAGCCUAAAGGUUCCAGCUGAAUCUUCCCAGGCAGGGCUGAAACAGGAACCAUUUUAGGCUUUGCUGCAACCCAUGGUCAGUUCUCCAAGAAAAGUGAAGAGGGUUCCACCUGGGGCAGCCCUCAAGGGCUCAGAGGGCCAAAACACACGUACAACAUGUUGAGACACUGAGUUUGUGCGAUCCCCACACAUCUCAGCAGUGAGUAUUUCUGCCUCAUUUUACCGAUGAGGAACCUGAGCUUCAAAGGGAAGAGGUGACAGCUCAGGACCACACAGCUGUAGGUAGGAGGCAGGAAAAUAGGGUCUGAGUGCAGGGAACAUAGGCUGAUUCACACUUCAGUUAUGAUAGGAAAUACCUUCUCCAUAGGACAUAGGCCAAGCAAAUGACUUUGUAACUUCAUCCUCUCCAUCUGCAUAACGUGUGCCCCAAGUAACCAAUGGAAUCACCUAGAGGGUGUUUAAACUCUCAGAAGUUCUGUAACAGGCUCUCCAUCUACAUAACGUGUGCCCCAAGUAACCAAUGGAAUCACCUAGAGGGUAUUUAAACUCUCUGAAGUUCUGUAACAGGGCUUUUGUGCUCCUAUGCUCAGGCUCACCCCCACACUGUGGAGUGUACUUUCAUUUUCAAUAAAUCCCUUCAUUCCUUCUUUGCUCUCUGUGUGUGUUUUGUCCAAUUCUUUAUUUAAGACGCCAAGAACCUGG',  # pylint: disable=line-too-long
        }
        self._check_results(query)

    def test_invalid_job_id(self):
        """
        Invalid job id.
        """
        job_id = 'foobar'
        url = self.base_url + reverse('nhmmer-job-results') + '?id=%s' % job_id
        r = requests.get(url)
        data = r.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['results'], [])


class RandomSearchesTests(NhmmerTestCase):
    """
    Use RNAcentral API to retrieve RNAcenrtal ids and sequences
    at random and use them to launch sequence searches.
    """
    num_tests = 5

    def get_random_query(self):
        """
        Get a random entry using the API.
        """
        url = self.base_url + reverse('rna-sequences')
        r = requests.get(url)
        total = r.json()['count']
        rna_url = url + '?page_size=1&page=%i' % randint(1, total)
        r = requests.get(rna_url)
        data = r.json()['results'][0]
        return {
            'id': data['rnacentral_id'],
            'sequence': data['sequence'],
        }

    def test_random_entries(self):
        """
        Run tests against a random entry.
        """
        for i in xrange(self.num_tests):
            query = self.get_random_query()
            self._check_results(query)


def setup_django_environment():
    """
    Setup Django environment in order for `reverse` and other Django
    functionality to work.
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
    parser.add_argument('--base_url', default='http://127.0.0.1:8000')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()

    if args.base_url[-1] == '/':
        args.base_url = args.base_url[:-1]
    NhmmerTestCase.base_url = args.base_url

    sys.argv[1:] = args.unittest_args

def run_tests():
    """
    Organize and run the test suites.
    """
    suites = [
        unittest.TestLoader().loadTestsFromTestCase(SubmitTests),
        unittest.TestLoader().loadTestsFromTestCase(GetStatusTests),
        unittest.TestLoader().loadTestsFromTestCase(ResultsTests),
        unittest.TestLoader().loadTestsFromTestCase(RandomSearchesTests),
    ]

    unittest.TextTestRunner().run(unittest.TestSuite(suites))

if __name__ == '__main__':
    setup_django_environment()
    parse_arguments()
    run_tests()
