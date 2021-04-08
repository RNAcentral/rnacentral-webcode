import json
from django.test import TestCase
from django.urls import resolve, reverse

from portal.views import homepage, rna_view, rna_view_redirect, expert_database_view, proxy, r2dt, get_sequence_lineage


class PortalTest(TestCase):
    def setUp(self):
        self.upi = 'URS0000000001'
        self.taxid = '77133'
        self.expert_db = 'mirbase'

    ########################
    # homepage
    ########################
    def test_homepage_url(self):
        view = resolve('/')
        self.assertEqual(view.func, homepage)

    def test_homepage_status_code(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_homepage_template(self):
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'portal/homepage.html')

    ########################
    # unique RNA sequence
    ########################
    def test_rna_view_url(self):
        view = resolve('/rna/' + self.upi)
        self.assertEqual(view.func, rna_view)

    def test_rna_view_status_code(self):
        response = self.client.get(reverse('unique-rna-sequence', kwargs={'upi': self.upi}))
        self.assertEqual(response.status_code, 200)

    def test_rna_view_404(self):
        response = self.client.get(reverse('unique-rna-sequence', kwargs={'upi': 'URS9999999999'}))
        self.assertEqual(response.status_code, 404)

    def test_rna_view_with_taxid_status_code(self):
        response = self.client.get(reverse('unique-rna-sequence', kwargs={'upi': self.upi, 'taxid': self.taxid}))
        self.assertEqual(response.status_code, 200)

    def test_rna_view_template(self):
        response = self.client.get(reverse('unique-rna-sequence', kwargs={'upi': self.upi}))
        self.assertTemplateUsed(response, 'portal/sequence.html')

    ########################
    # species specific identifier with underscore
    ########################
    def test_rna_view_redirect_url(self):
        view = resolve('/rna/' + self.upi + '_' + self.taxid)
        self.assertEqual(view.func, rna_view_redirect)

    def test_rna_view_redirect_status_code(self):
        response = self.client.get(
            reverse('unique-rna-sequence-redirect', kwargs={'upi': self.upi, 'taxid': self.taxid})
        )
        self.assertEqual(response.status_code, 301)

    ########################
    # expert database
    ########################
    def test_expert_database_view_url(self):
        view = resolve('/expert-database/' + self.expert_db)
        self.assertEqual(view.func, expert_database_view)

    def test_expert_database_status_code(self):
        response = self.client.get(reverse('expert-database', kwargs={'expert_db_name': self.expert_db}))
        self.assertEqual(response.status_code, 200)

    def test_expert_database_404(self):
        response = self.client.get(reverse('expert-database', kwargs={'expert_db_name': 'test'}))
        self.assertEqual(response.status_code, 404)

    def test_expert_database_template(self):
        response = self.client.get(reverse('expert-database', kwargs={'expert_db_name': 'tmrna-website'}))
        self.assertTemplateUsed(response, 'portal/expert-database.html')

    ########################
    # text search
    ########################
    def test_text_search_status_code(self):
        response = self.client.get(reverse('text-search'))
        self.assertEqual(response.status_code, 200)

    def test_text_search_template(self):
        response = self.client.get(reverse('text-search'))
        self.assertTemplateUsed(response, 'portal/base.html')

    ########################
    # downloads
    ########################
    def test_downloads_status_code(self):
        response = self.client.get(reverse('downloads'))
        self.assertEqual(response.status_code, 200)

    def test_downloads_template(self):
        response = self.client.get(reverse('downloads'))
        self.assertTemplateUsed(response, 'portal/downloads.html')

    ########################
    # external link
    ########################
    # TODO: get an example link
    def _test_external_link_status_code(self):
        response = self.client.get(reverse('external-link', kwargs={'expert_db': self.expert_db, 'external_id': 1}))
        self.assertEqual(response.status_code, 200)

    ########################
    # help pages
    ########################
    def test_help_status_code(self):
        response = self.client.get(reverse('help'))
        self.assertEqual(response.status_code, 200)

    def test_help_browser_compatibility_status_code(self):
        response = self.client.get(reverse('help-browser-compatibility'))
        self.assertEqual(response.status_code, 200)

    def test_help_text_search_status_code(self):
        response = self.client.get(reverse('help-text-search'))
        self.assertEqual(response.status_code, 200)

    def test_help_rfam_annotations_status_code(self):
        response = self.client.get(reverse('help-rfam-annotations'))
        self.assertEqual(response.status_code, 200)

    def test_help_rna_target_interactions_status_code(self):
        response = self.client.get(reverse('help-rna-target-interactions'))
        self.assertEqual(response.status_code, 200)

    def test_help_gene_ontology_annotations_status_code(self):
        response = self.client.get(reverse('help-gene-ontology-annotations'))
        self.assertEqual(response.status_code, 200)

    def test_help_genomic_mapping_status_code(self):
        response = self.client.get(reverse('help-genomic-mapping'))
        self.assertEqual(response.status_code, 200)

    def test_linking_to_rnacentral_status_code(self):
        response = self.client.get(reverse('linking-to-rnacentral'))
        self.assertEqual(response.status_code, 200)

    def test_help_conserved_motifs_status_code(self):
        response = self.client.get(reverse('help-conserved-motifs'))
        self.assertEqual(response.status_code, 200)

    def test_help_public_database_status_code(self):
        response = self.client.get(reverse('help-public-database'))
        self.assertEqual(response.status_code, 200)

    def test_help_scientific_advisory_board_status_code(self):
        response = self.client.get(reverse('help-scientific-advisory-board'))
        self.assertEqual(response.status_code, 200)

    def test_help_secondary_structure_status_code(self):
        response = self.client.get(reverse('help-secondary-structure'))
        self.assertEqual(response.status_code, 200)

    def test_help_sequence_search_status_code(self):
        response = self.client.get(reverse('help-sequence-search'))
        self.assertEqual(response.status_code, 200)

    def test_help_galaxy_status_code(self):
        response = self.client.get(reverse('help-galaxy'))
        self.assertEqual(response.status_code, 200)

    ########################
    # training, about-us, use-cases, api, contact, thanks, error
    ########################
    def test_training_status_code(self):
        response = self.client.get(reverse('training'))
        self.assertEqual(response.status_code, 200)

    def test_about_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_use_cases_status_code(self):
        response = self.client.get(reverse('use-cases'))
        self.assertEqual(response.status_code, 200)

    def test_api_docs_status_code(self):
        response = self.client.get(reverse('api-docs'))
        self.assertEqual(response.status_code, 200)

    def test_contact_us_status_code(self):
        response = self.client.get(reverse('contact-us'))
        self.assertEqual(response.status_code, 200)

    def test_thanks_status_code(self):
        response = self.client.get(reverse('contact-us-success'))
        self.assertEqual(response.status_code, 200)

    def test_error_status_code(self):
        response = self.client.get(reverse('error'))
        self.assertEqual(response.status_code, 200)

    ########################
    # website status
    ########################
    def test_website_status_status_code(self):
        response = self.client.get(reverse('website-status'))
        self.assertEqual(response.status_code, 200)

    def test_website_status_template(self):
        response = self.client.get(reverse('website-status'))
        self.assertTemplateUsed(response, 'portal/website-status.html')

    ########################
    # genome browser
    ########################
    def test_genome_browser_status_code(self):
        response = self.client.get(reverse('genome-browser'))
        self.assertEqual(response.status_code, 200)

    def test_genome_browser_wrong_specie(self):
        response = self.client.get('/genome-browser', {'species': 'test'})
        self.assertEqual(response.status_code, 404)

    def test_genome_browser_with_chromosome_start_end(self):
        response = self.client.get(
            '/genome-browser', {'species': 'homo_sapiens', 'chromosome': 'X', 'start': '73819307', 'end':'73856333'}
        )
        self.assertEqual(response.status_code, 200)

    def test_genome_browser_with_chr_start_end(self):
        response = self.client.get(
            '/genome-browser', {'species': 'homo_sapiens', 'chr': 'X', 'start': '73819307', 'end':'73856333'}
        )
        self.assertEqual(response.status_code, 200)

    def test_genome_browser_template(self):
        response = self.client.get(reverse('genome-browser'))
        self.assertTemplateUsed(response, 'portal/genome-browser.html')

    ########################
    # proxy
    ########################
    def test_proxy_view_url(self):
        view = resolve('/api/internal/proxy/')
        self.assertEqual(view.func, proxy)

    def test_proxy_forbidden(self):
        response = self.client.get('/api/internal/proxy/', {'url': 'https://example.com'})
        self.assertEqual(response.status_code, 403)

    def test_proxy_invalid_request(self):
        response = self.client.get(
            '/api/internal/proxy/', {'url': 'https://www.ebi.ac.uk/api/internal/proxy?url=http://example.com'}
        )
        self.assertEqual(response.status_code, 404)

    ########################
    # r2dt
    ########################
    def test_r2dt_view_url(self):
        view = resolve('/r2dt')
        self.assertEqual(view.func, r2dt)

    def test_r2dt_status_code(self):
        response = self.client.get(reverse('r2dt'))
        self.assertEqual(response.status_code, 200)

    def test_r2dt_template(self):
        response = self.client.get(reverse('r2dt'))
        self.assertTemplateUsed(response, 'portal/r2dt.html')

    ########################
    # get species tree
    ########################
    def test_get_sequence_lineage_view_url(self):
        view = resolve('/rna/' + self.upi + '/lineage')
        self.assertEqual(view.func, get_sequence_lineage)

    def test_get_sequence_lineage_status_code(self):
        response = self.client.get(reverse('sequence-lineage', kwargs={'upi': self.upi}))
        self.assertEqual(response.status_code, 200)

    def test_get_sequence_lineage_no_results(self):
        response = self.client.get(reverse('sequence-lineage', kwargs={'upi': 'URS9999999999'}))
        self.assertEqual(json.loads(response.content), {'name': 'All', 'children': []})
