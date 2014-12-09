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
Test exporting search results.

Usage:

# test localhost
python export_results_tests.py

# test an RNAcentral instance
python export_results_tests.py --base_url http://test.rnacentral.org/
"""

import argparse
import django
import os
import requests
import sys
import unittest

from django.core.urlresolvers import reverse


class ExportSearchResultsTest(unittest.TestCase):
    """Unit tests entry point"""
    base_url = ''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_download_no_job_id(self):
        """
        No job id is provided in the url.
        """
        url = self.base_url + reverse('export-download-result')
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_download_invalid_job_id(self):
        """
        Invalid job id or job id not found.
        """
        job_id = 'foobar'
        url = self.base_url + reverse('export-download-result') + '?job=%s' % job_id
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'rnacentral.settings'
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    sys.path.append(project_dir)
    django.setup()

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_url', default='http://127.0.0.1:8000')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    if args.base_url[-1] == '/':
        args.base_url = args.base_url[:-1]
    ExportSearchResultsTest.base_url = args.base_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
