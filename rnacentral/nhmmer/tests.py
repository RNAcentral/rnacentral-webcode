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
import unittest

from django.core.urlresolvers import reverse

from messages import messages


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
        sequence = 'AUCG' * 1000
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

    def test_get_status_no_job_id(self):
        """
        No job id is provided in the url.
        """
        url = self.base_url + reverse('nhmmer-job-status')
        status = 400
        message = messages[self.msg_type][status]['message']
        r = requests.get(url)
        self.assertEqual(r.status_code, status)
        self.assertEqual(r.json()['message'], message)

    def test_get_status_invalid_job_id(self):
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

    def test_get_status_valid_job(self):
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
    ]

    unittest.TextTestRunner().run(unittest.TestSuite(suites))

if __name__ == '__main__':
    setup_django_environment()
    parse_arguments()
    run_tests()
