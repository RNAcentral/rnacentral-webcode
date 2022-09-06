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

import json

import requests
from django.test import TestCase
from django.urls import reverse


class ExportSearchResultsTestCase(TestCase):
    """
    Base class for export search results testing.
    Using the test website because I don't want to run redis locally for now.
    """

    base_url = "https://test.rnacentral.org"

    def setUp(self):
        self.queries = {
            "small": "hotair",
        }

    def _submit_query(self, query, _format=""):
        """
        Submit a query and return the response object.
        """
        url = "".join(
            [
                self.base_url,
                reverse("export-submit-job"),
                "?q=%s" % query,
                "&format=%s" % _format if _format else "",
            ]
        )
        return requests.get(url)


class SubmitExportTests(ExportSearchResultsTestCase):
    """
    Tests for the job submission endpoint.
    """

    def test_submit_empty_query(self):
        """
        No query is provided in the url.
        """
        r = self._submit_query(query="")
        self.assertEqual(r.status_code, 400)

    def test_submit_invalid_format(self):
        """
        Invalid export format.
        """
        r = self._submit_query(query=self.queries["small"], _format="bar")
        self.assertEqual(r.status_code, 404)

    def test_submit_export_job(self):
        """
        Submit a small query in multiple formats.
        """
        formats = ["fasta", "json", ""]
        query = self.queries["small"]
        for _format in formats:
            r = self._submit_query(query=query, _format=_format)
            data = json.loads(r.text)
            self.assertEqual(r.status_code, 200)
            self.assertIn("job_id", data)


class GetStatusTests(ExportSearchResultsTestCase):
    """
    Tests for the job status endpoint.
    """

    def test_get_status_no_job_id(self):
        """
        No job id is provided in the url.
        """
        url = self.base_url + reverse("export-job-status")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_get_status_invalid_job_id(self):
        """
        Invalid job id or job id not found.
        """
        job_id = "foobar"
        url = self.base_url + reverse("export-job-status") + "?job=%s" % job_id
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)

    def test_get_status_valid_job(self):
        """
        Submit a small query and check its status.
        """
        r = self._submit_query(query=self.queries["small"])
        job_id = json.loads(r.text)["job_id"]
        url = self.base_url + reverse("export-job-status") + "?job=%s" % job_id
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)


class DownloadResultsTests(ExportSearchResultsTestCase):
    """
    Tests for the download results endpoint.
    """

    def test_download_no_job_id(self):
        """
        No job id is provided in the url.
        """
        url = self.base_url + reverse("export-download-result")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_download_invalid_job_id(self):
        """
        Invalid job id or job id not found.
        """
        job_id = "foobar"
        url = "".join(
            [self.base_url, reverse("export-download-result"), "?job=%s" % job_id]
        )
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)


class ResultsPageTests(ExportSearchResultsTestCase):
    def test_results_status_code(self):
        response = self.client.get(reverse("export-job-results"))
        self.assertEquals(response.status_code, 200)

    def test_results_template(self):
        response = self.client.get(reverse("export-job-results"))
        self.assertTemplateUsed(response, "portal/search/export-job-results.html")
