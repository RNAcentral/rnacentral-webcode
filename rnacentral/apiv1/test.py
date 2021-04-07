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

import time

from django.conf import settings
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient


class Timer(object):
    """Helper class for detecting long-running requests."""
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.timeout = self.end - self.start


class ApiV1BaseClass(APITestCase):
    """Base class for API tests."""
    upi = 'URS0000000001'
    upi_with_genomic_coordinates = 'URS00000B15DA'
    upi_with_svg = 'URS0000704D22'
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
    * /rna/id/related-protein
    * /rna/id/2d/svg
    """
    def test_rna_list(self):
        """Test RNA list (hyperlinked response)."""
        url = reverse('rna-sequences')
        self._test_url(url)

    def test_rna_list_filter_by_database(self):
        """Test filter by database (hyperlinked response)."""
        url = reverse('rna-sequences')
        self._test_url(url, data={'database': 'mirbase'})

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
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_xref_pagination(self):
        """Ensure that xrefs can be paginated."""
        upi = 'URS000075A546'  # >150 xrefs
        page = 4
        page_size = 2
        url = reverse('rna-xrefs', kwargs={'pk': upi})
        response = self._test_url(url, data={'page': page, 'page_size': page_size})
        self.assertTrue(len(response.data['results']), page_size)

    def test_related_proteins(self):
        """Test RNA proteins endpoint."""
        upi = 'URS0000013DD8'  # >270 related proteins
        taxid = '9606'
        page = 1
        page_size = 1000
        url = reverse('rna-protein-targets', kwargs={'pk': upi, 'taxid': taxid})
        with Timer() as timer:
            c = APIClient()
            response = c.get(url, data={'page': page, 'page_size': page_size})
        self.assertTrue(timer.timeout < 10)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['results']) > 200)

    def test_related_proteins_pagination(self):
        upi = 'URS0000021B51'  # over 9000 entries =)
        taxid = '10090'
        url = reverse('rna-protein-targets', kwargs={'pk': upi, 'taxid': taxid})
        with Timer() as timer:
            c = APIClient()
            response = c.get(url, data={})  # pagination is enabled by default
        # self.assertTrue(timer.timeout < 2)  # paginated request has to be fast, but it takes a little more than 2 sec
        self.assertGreater(response.data['count'], 8000)  # well, not quite 'over 9000', but still many...
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['results']) == settings.REST_FRAMEWORK['PAGE_SIZE'])

    def test_rna_sequence_features(self):
        """Test RNA sequence features endpoint"""
        upi = "URS00008B3580"
        taxid = "9606"
        url = reverse('rna-sequence-features', kwargs={'pk': upi, 'taxid': taxid})
        response = self._test_url(url)
        self.assertGreater(response.data['count'], 0)

    def test_rna_svg_image(self):
        """Test SVG endpoint."""
        url = reverse('rna-2d-svg', kwargs={'pk': self.upi_with_svg})
        self._test_url(url)

    def test_rna_svg_image_404(self):
        """Test endpoint for 404 status code."""
        response = self.client.get(reverse('rna-2d-svg', kwargs={'pk': 'URS0000000002'}))
        self.assertEqual(response.status_code, 404)

    def test_rna_xrefs_species_specific(self):
        """Test rna-xrefs-species-specific endpoint."""
        url = reverse('rna-xrefs-species-specific', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_rna_2d_species_specific(self):
        """Test rna-2d-species-specific endpoint."""
        url = reverse('rna-2d-species-specific', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_rna_rfam_hits(self):
        """Test rna-rfam-hits endpoint."""
        url = reverse('rna-rfam-hits', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_rna_genome_locations(self):
        """Test rna-genome-locations endpoint."""
        url = reverse('rna-genome-locations', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_rna_go_annotations(self):
        """Test rna-go-annotations endpoint."""
        url = reverse('rna-go-annotations', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_ensembl_compara(self):
        """Test ensembl-compara endpoint."""
        url = reverse('rna-ensembl-compara', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_rna_lncrna_targets(self):
        """Test rna-lncrna-targets endpoint."""
        url = reverse('rna-lncrna-targets', kwargs={'pk': 'URS00006457C1', 'taxid': '10090'})
        self._test_url(url)

    def test_expert_dbs_api(self):
        """Test expert-dbs-api endpoint."""
        url = reverse('expert-dbs-api')
        self._test_url(url)

    def test_ensembl_karyotype(self):
        """Test ensembl-karyotype endpoint."""
        url = reverse('ensembl-karyotype', kwargs={'ensembl_url': 'fusarium_verticillioides'})
        self._test_url(url)


class NestedXrefsTestCase(ApiV1BaseClass):
    """Test flat/hyperlinked pagination."""
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

    # TODO: Find another UPI to test
    def _test_mirbase_mature_products(self):
        self._test_time_and_existence('URS0000759B7E', self.timeout, "mirbase_mature_products")

    def test_mirbase_precursor(self):
        self._test_time_and_existence('URS00006457C1', self.timeout, "mirbase_precursor")

    # TODO: Find another UPI to test
    def _test_refseq_mirna_mature_products(self):
        self._test_time_and_existence('URS000075A546', self.timeout, "refseq_mirna_mature_products")

    # TODO: Find another UPI to test
    def _test_refseq_mirna_precursor(self):
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

    def test_genome_annotations(self):
        """
        Test the Ensembl-like endpoint for retrieving data
        based on genome coordinates.
        `feature` was replaced with `overlap` in Ensembl.
        """
        # Django cannot reverse a URL that contains alternative choices using the vertical bar ("|") character.
        # url = reverse(
        #     'human-genome-coordinates',
        #     kwargs={'species': 'homo_sapiens', 'chromosome': '2', 'start': '39,745,816', 'end': '39,826,679'}
        # )

        response = self._test_url('/api/v1/overlap/region/homo_sapiens/2:39,745,816-39,826,679')
        self.assertNotEqual(len(response.data), 0)

        for annotation in response.data:
            if annotation['feature_type'] == 'transcript':
                self.assertIn('URS', annotation['external_name'])
            elif annotation['feature_type'] == 'exon':
                self.assertIn('URS', annotation['Parent'])
            else:
                self.assertEqual(0, 1, "Unknown genomic annotation type")

    def test_genome_annotations_empty_data(self):
        response = self._test_url('/api/v1/overlap/region/homo_sapiens/0:0,0,0-0,0,0')
        self.assertEqual(len(response.data), 0)


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

    # TODO: check portal/models/database.py file, line 110. GENCODE was renamed.
    def _test_bad_database_filter(self):
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

    def test_species_specific_id(self):
        """Get an existing upi and taxid."""
        url = reverse('rna-species-specific', kwargs={'pk': self.upi, 'taxid': str(self.taxid)})
        c = APIClient()
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['rnacentral_id'], '%s_%i' % (self.upi, self.taxid))
        self.assertEqual(response.data['is_active'], True)

    def test_nonexistent_taxid(self):
        """Non-existent taxid should return a 404 error."""
        taxid = 00000
        url = reverse('rna-species-specific', kwargs={'pk': self.upi, 'taxid': str(taxid)})
        c = APIClient()
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

    def test_inactive_entry(self):
        """
        When there are no active xrefs for a taxid,
        the `is_active` field should be `False`.
        """
        upi = 'URS0000F97F96'
        url = reverse('rna-detail', kwargs={'pk': upi})
        c = APIClient()
        response = c.get(url)
        self.assertEqual(response.data['is_active'], False)


class GenomesTestCase(ApiV1BaseClass):
    """Tests for ensembl assemblies."""
    def test_list(self):
        url = reverse('genomes-api')
        response = self._test_url(url)
        self.assertEqual(response.status_code, 200)
