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
    """Helper class for detecting long-running requests."""
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


class OutputFormatsTestCase(ApiV1BaseClass):
    """Test output formats."""
    def _output_format_tester(self, formats, urls):
        """
        Test all possible ways of specifying output format:
        * suffix, e.g. ".json"
        * url notation, e.g. "?format=json"
        * accept headers
        """
        c = APIClient()
        for url in urls:
            for suffix, headers in six.iteritems(formats):
                request = c.get(url + '.%s' % suffix)  # format suffix
                self.assertEqual(request.status_code, 200, url)
                request = c.get(url + '?format=%s' % suffix)  # url notation
                self.assertEqual(request.status_code, 200, url)
                request = c.get(url, headers={"Accept": headers})  # accept headers
                self.assertEqual(request.status_code, 200, url)

    def test_json_yaml_api_formats(self):
        """Test json/yaml/api formats."""
        formats = {'json': 'application/json',
                   'yaml': 'application/yaml',
                   'api': 'text/html'}
        urls = (
            reverse('rna-sequences'),
            reverse('rna-detail', kwargs={'pk': self.upi}),
            reverse('rna-xrefs', kwargs={'pk': self.upi}),
            reverse('accession-detail', kwargs={'pk': self.accession}),
            reverse('accession-citations', kwargs={'pk': self.accession})
        )

        self._output_format_tester(formats, urls)

    def test_fasta_output(self):
        """Test fasta format."""
        formats = {'fasta': 'text/fasta'}

        urls = (
            reverse('rna-sequences'),
            reverse('rna-detail', kwargs={'pk': self.upi})
        )

        self._output_format_tester(formats, urls)

    def test_gff_output(self):
        """Test gff output."""
        c = APIClient()
        formats = {'gff': 'text/gff'}

        urls = (
            reverse('rna-detail', kwargs={'pk': self.upi_with_genomic_coordinates}),
            reverse('rna-detail', kwargs={'pk': self.upi}),
        )

        # test response status codes
        self._output_format_tester(formats, urls)

        # further check the gff text output
        response = c.get(urls[0] + '.gff')
        self.assertIn('exon', response.content)

        # test a sequence without genomic coordinates
        response = c.get(urls[1] + '.gff')
        self.assertIn('# Genomic coordinates not available', response.content)

    def test_gff3_output(self):
        """Test gff3 output."""
        c = APIClient()
        formats = {'gff3': 'text/gff3'}
        urls = (
            reverse('rna-detail', kwargs={'pk': self.upi_with_genomic_coordinates}),
            reverse('rna-detail', kwargs={'pk': self.upi}),
        )

        # test response status codes
        self._output_format_tester(formats, urls)

        # further check the gff text output
        response = c.get(urls[0] + '.gff3')
        self.assertIn('noncoding_exon', response.content)

        # test a sequence without genomic coordinates
        response = c.get(urls[1] + '.gff3')
        self.assertIn('# Genomic coordinates not available', response.content)

    def test_bed_output(self):
        """Test bed output."""
        c = APIClient()
        formats = {'bed': 'text/bed'}
        urls = (
            reverse('rna-detail', kwargs={'pk': self.upi_with_genomic_coordinates}),
            reverse('rna-detail', kwargs={'pk': self.upi}),
        )

        # test response status codes
        self._output_format_tester(formats, urls)

        # further check the gff text output
        response = c.get(urls[0] + '.bed')
        self.assertIn(self.upi_with_genomic_coordinates, response.content)

        # test a sequence without genomic coordinates
        response = c.get(urls[1] + '.bed')
        self.assertIn('# Genomic coordinates not available', response.content)

    # TODO: something wrong with reverse()
    # def test_genome_annotations(self):
    #     """
    #     Test the Ensembl-like endpoint for retrieving data
    #     based on genome coordinates.
    #     `feature` was replaced with `overlap` in Ensembl.
    #     """
    #     urls = [
    #         reverse('human-genome-coordinates',
    #                 kwargs={'species': 'homo_sapiens', 'chromosome': 'Y', 'start': '25,183,643', 'end': '25,184,773'}),
    #         reverse('human-genome-coordinates',
    #                 kwargs={'species': 'homo_sapiens', 'chromosome': '2', 'start': '39,745,816', 'end': '39,826,679'})
    #     ]
    #
    #     for url in urls:
    #         data = self._test_url(url)
    #         self.assertNotEqual(len(data), 0)
    #         for annotation in data:
    #             if annotation['feature_type'] == 'transcript':
    #                 self.assertIn('URS', annotation['external_name'])
    #             elif annotation['feature_type'] == 'exon':
    #                 self.assertIn('URS', annotation['Parent'])
    #             else:
    #                 self.assertEqual(0, 1, "Unknown genomic annotation type")


class FiltersTestCase(ApiV1BaseClass):
    """Test url parameter filters."""
    def test_rna_md5_filter(self):
        """Test md5 filter."""
        url = reverse('rna-sequences')
        response = self._test_url(url, data={'md5': self.md5})
        self.assertEqual(response.data['results'][0]['rnacentral_id'], self.upi)

    def test_rna_upi_filter(self):
        """Test filtering by RNAcentral id."""
        url = reverse('rna-detail', kwargs={'pk': self.upi})
        response = self._test_url(url)
        self.assertEqual(response.data['md5'], self.md5)

    def test_rna_length_filter(self):
        """Test filtering by sequence length."""
        filters = [
            {'min_length': '200000'},
            {'length': '2014'},
            {'max_length': '11'},
            {'min_length': '11', 'max_length': '12'},
        ]

        for filter in filters:
            url = reverse('rna-sequences')
            response = self._test_url(url, data=filter)
            self.assertNotEqual(response.data['count'], 0)

    # TODO: database filter doesn't work
    # def test_rna_database_filter(self):
    #     """Test filtering by database name."""
    #     for database in ['gtrnadb', 'srpdb', 'snopy']:
    #         url = reverse('rna-sequences')
    #         response = self._test_url(url, data={'database': database})
    #         self.assertNotEqual(response.data['count'], 0)

    def test_bad_database_filter(self):
        """Test filtering by database name when database name does not exist."""
        url = reverse('rna-sequences')
        response = self._test_url(url, data={'database': 'test'})
        self.assertEqual(response.data['count'], 0)

    def test_rna_external_id_filter(self):
        """Test filtering by external id."""
        external_ids = [
            'Stap.epid._AF269831', # SRPDB
            'MIMAT0000091', # miRBase
            'OTTHUMG00000172092', # Vega
            'Lepto_inter_Lai566', # tmRNA Website
            '1J5E', # PDB
            'NR_029645', # RefSeq
        ]
        for external_id in external_ids:
            url = reverse('rna-sequences')
            response = self._test_url(url, data={'external_id': external_id})
            self.assertNotEqual(response.data['count'], 0, 'Failed on %s' % url)


class SpeciesSpecificIdsTestCase(ApiV1BaseClass):
    """Tests for the species-specific endpoints."""
    upi = 'URS000047C79B'
    taxid = 9606

    # TODO: can't resolve species-specific url
    # def test_species_specific_id(self):
    #     """Get an existing upi and taxid."""
    #     url = reverse('rna-species-specific', kwargs={'pk': self.upi, 'taxid': str(self.taxid)})
    #     c = APIClient()
    #     response = c.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['rnacentral_id'], '%s_%i' % (self.upi, self.taxid))
    #     self.assertEqual(response.data['is_active'], True)
    #
    # def test_nonexistent_taxid(self):
    #     """Non-existent taxid should return a 404 error."""
    #     taxid = 00000
    #     url = reverse('rna-species-specific', kwargs={'pk': self.upi, 'taxid': str(taxid)})
    #     c = APIClient()
    #     response = c.get(url)
    #     self.assertEqual(response.status_code, 404)

    def test_inactive_entry(self):
        """
        When there are no active xrefs for a taxid,
        the `is_active` field should be `False`.
        """
        upi = 'URS0000516D2D'
        url = reverse('rna-detail', kwargs={'pk': upi})
        c = APIClient()
        response = c.get(url)
        self.assertEqual(response.data['is_active'], False)