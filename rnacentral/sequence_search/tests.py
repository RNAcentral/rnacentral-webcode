from django.test import TestCase
from django.urls import resolve, reverse
from mock import patch, Mock

from sequence_search.views import dashboard, show_searches


class SequenceSearchTest(TestCase):
    def setUp(self):
        self.data = [
            {"count": 15, "avg_time": "0:02:47", "search": "all"},
            {"count": 0, "avg_time": 0, "search": "last-24-hours"},
            {"count": 3, "avg_time": "0:02:19", "search": "last-week"}
        ]

    def test_show_searches_url(self):
        view = resolve('/sequence-search-beta/show-searches')
        self.assertEquals(view.func, show_searches)

    def test_dashboard_url(self):
        view = resolve('/sequence-search-beta/dashboard')
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
