from django.test import TestCase
from django.urls import resolve, reverse
from mock import patch, Mock

from sequence_search.views import dashboard, show_searches


class SequenceSearchTest(TestCase):
    def setUp(self):
        self.data = {
            "all_searches_result": {"count": 14602, "avg_time": "0:01:10"},
            "last_24_hours_result": {"count": 118, "avg_time": "0:04:07"},
            "last_week_result": {"count": 896, "avg_time": "0:00:46"},
            "searches_per_month": [],
            "expert_db_results": [{"RNAcentral": []}, {"Rfam": []}, {"miRBase": []}, {"snoDB": []}, {"GtRNAdb": []}]
        }

    def test_show_searches_url(self):
        view = resolve('/sequence-search/show-searches')
        self.assertEquals(view.func, show_searches)

    def test_dashboard_url(self):
        view = resolve('/sequence-search/dashboard')
        self.assertEquals(view.func, dashboard)

    @patch('requests.get')
    def test_dashboard_status_code(self, mock_get):
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.data
        response = self.client.get(reverse('sequence-search-dashboard'))
        self.assertEquals(response.status_code, 200)

    @patch('requests.get')
    def test_dashboard_template_used(self, mock_get):
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.data
        response = self.client.get(reverse('sequence-search-dashboard'))
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_help_page_status_code(self):
        response = self.client.get(reverse('help-sequence-search'))
        self.assertEquals(response.status_code, 200)

    def test_help_page_template(self):
        response = self.client.get(reverse('help-sequence-search'))
        self.assertTemplateUsed(response, 'portal/help/sequence-search-help.html')

    def test_sequence_search_api_status_code(self):
        response = self.client.get(reverse('sequence-search-api'))
        self.assertEquals(response.status_code, 200)

    def test_sequence_search_api_template(self):
        response = self.client.get(reverse('sequence-search-api'))
        self.assertTemplateUsed(response, 'api.html')

    def test_sequence_search_status_code(self):
        response = self.client.get(reverse('sequence-search'))
        self.assertEquals(response.status_code, 200)

    def test_sequence_search_template(self):
        response = self.client.get(reverse('sequence-search'))
        self.assertTemplateUsed(response, 'sequence-search-embed.html')
