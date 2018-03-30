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
from __future__ import print_function
import six

from random import randint
import argparse
import math
import os
import sys
import time
import unittest

import django
import requests
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient


class Timer(object):
    """
    Helper class for detecting long-running requests.
    """
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.timeout = (self.end - self.start) * 100


class ApiV1BaseClass(APITestCase):
    """Base class for API tests."""
    upi = 'URS0000000001'
    upi_with_genomic_coordinates = 'URS00000B15DA'
    md5 = '6bba097c8c39ed9a0fdf02273ee1c79a'  # URS0000000001
    accession = 'Y09527.1:2562..2627:tRNA'
    timeout = 60  # seconds

    def _test_url(self, url, data=None, follow=False, **extra):
        """Auxiliary function for testing the API with and without trailing slash."""
        c = APIClient()
        response = c.get(url, data=data, follow=follow, **extra)
        self.assertEqual(response.status_code, 200)
        return response


class BasicEndpointsTestCase(ApiV1BaseClass):
    """Basic tests for generic endpoints."""
    def test_current_api_endpoint(self):
        """Stable endpoint for the latest version of the API."""
        c = APIClient()
        response = c.get('/api/current/')
        self.assertEqual(response.status_code, 200)

    def test_api_v1_endpoint(self):
        """Test API v1 endpoint."""
        url = reverse('api-v1-root')
        self._test_url(url)


class AccessionEndpointsTestCase(ApiV1BaseClass):
    """
    Test Accession endpoints.
    * /accession/id/info
    * /accession/id/citations
    """
    def test_accession_entry(self):
        """Test accession info endpoint."""
        url = reverse('accession-detail', kwargs={'pk': self.accession})
        self._test_url(url)

    def test_accession_citations(self):
        """Test accession citations endpoint."""
        url = reverse('accession-citations', kwargs={'pk': self.accession})
        self._test_url(url)


class RnaEndpointsTestCase(ApiV1BaseClass):
    """
    Test RNA endpoints
    * /rna
    * /rna/id/xrefs
    * /rna/id/publications
    """
    def test_rna_list(self):
        """Test RNA list (hyperlinked response)."""
        url = reverse('rna-sequences')
        self._test_url(url)

    def test_rna_list_pagination(self):
        """Test paginated RNA list (hyperlinked response)."""
        page = 10
        page_size = 5
        url = reverse('rna-sequences')
        response = self._test_url(url, data={'page': page, 'page_size': page_size})
        self.assertEqual(len(response.data['results']), page_size)

    def test_rna_sequence(self):
        """Test RNA entry (hyperlinked response)."""
        url = reverse('rna-detail', kwargs={'pk': self.upi})
        response = self._test_url(url)
        self.assertEqual(response.data['md5'], self.md5)
        self.assertEqual(response.data['length'], 200)

    def test_rna_xrefs(self):
        """Test RNA xrefs endpoint."""
        url = reverse('rna-xrefs', kwargs={'pk': self.upi})
        self._test_url(url)

    def test_rna_publications(self):
        """Test RNA publications endpoint."""
        url = reverse('rna-publications', kwargs={'pk': self.upi})
        response = self._test_url(url)
        self.assertEqual(len(response.data['results']), 1)

    def test_xref_pagination(self):
        """Ensure that xrefs can be paginated."""
        upi = 'URS000075A546'  # >150 xrefs
        page = 4
        page_size = 2
        url = reverse('rna-xrefs', kwargs={'pk': upi})
        response = self._test_url(url, data={'page': page, 'page_size': page_size})
        self.assertTrue(len(response.data['results']), page_size)


class NestedXrefsTestCase(ApiV1BaseClass):
    """Test flat/hyperlinked pagination."""
    # TODO: this test is failing due to change in DRF3 pagination API
    # def test_hyperlinked_responses(self):
    #     """Test hyperlinked response explicitly specified in the url."""
    #     url = reverse('rna-sequences')
    #     response = self._test_url(url, data={'flat': False})
    #     self.assertIn('http', response.data['results'][0]['xrefs'])

    def test_flat_response(self):
        """Test flat response explicitly specified in the url."""
        url = reverse('rna-detail', kwargs={'pk': self.upi})
        response = self._test_url(url, data={'flat': True})
        self.assertNotEqual(len(response.data['xrefs']), 0)

    def test_large_nested_rna(self):
        """
        For nested responses only a subset of xrefs is included
        in the original response and the rest can be paginated
        in separate requests.
        """
        upi = 'URS000065859A'  # >200,000 xrefs
        url = reverse('rna-detail', kwargs={'pk': upi})
        response = self._test_url(url, data={'flat': True})
        self.assertTrue(len(response.data['xrefs']) == 100)

    # TODO: this test is failing due to change in DRF3 pagination API
    # def test_large_nested_page(self):
    #     """Ensure that xrefs can be paginated."""
    #     page = 115
    #     page_size = 100
    #     url = reverse('rna-sequences')
    #     response = self._test_url(url, data={'page': page, 'page_size': page_size, 'flat': True})
    #     self.assertTrue(len(response.data['results']), page_size)


class DatabaseSpecificXrefsTestCase(ApiV1BaseClass):
    """
    Test correctness and performance of Xref fields like:

        * modifications
        * mirbase_mature_products
        * mirbase_precursor
        * refseq_mirna_mature_products
        * refseq_mirna_precursor
        * refseq_splice_variants
        * tmrna_mate_upi
        * genomic_coordinates
    """
    timeout = 15

    def _test_time_and_existence(self, upi, timeout, field):
        """
        Shortcut to check that response time is tolerable and expected field
        is not empty.

        :param upi: upi of RNA to perform test on
        :param timeout: API should be fast enough to respond before
          this timeout expires (in seconds, e.g. 5)
        :param field: name of the field that we want to be non-empty at least
          for some Xrefs (e.g. "modifications")
        :return:
        """
        url = reverse('rna-xrefs', kwargs={'pk': upi})
        with Timer() as timer:
            c = APIClient()
            response = c.get(url)
        self.assertTrue(timer.timeout < timeout)
        self.assertEqual(response.status_code, 200)

        # check that field is non-empty at least for some results
        empty = True
        for xref in response.json()['results']:
            if xref[field] != None:
                empty = False
                break
        self.assertFalse(empty)

    def test_modifications(self):
        self._test_time_and_existence('URS00004B0F34', self.timeout, "modifications")

    def test_mirbase_mature_products(self):
        self._test_time_and_existence('URS000075A546', self.timeout, "mirbase_mature_products")

    def test_mirbase_precursor(self):
        self._test_time_and_existence('URS0000057A7C', self.timeout, "mirbase_precursor")

    def test_refseq_mirna_mature_products(self):
        self._test_time_and_existence('URS000075A546', self.timeout, "refseq_mirna_mature_products")

    def test_refseq_mirna_precursor(self):
        self._test_time_and_existence('URS0000416056', self.timeout, "refseq_mirna_precursor")

    def test_refseq_splice_variants(self):
        self._test_time_and_existence('URS000075C808', self.timeout, "refseq_splice_variants")
