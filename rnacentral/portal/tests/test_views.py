from django.test import TestCase
from django.urls import resolve, reverse

from portal.views import homepage, rna_view, rna_view_redirect, expert_database_view


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
