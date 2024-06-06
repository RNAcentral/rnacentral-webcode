import re

import requests
from django.test import TestCase


class TestVersionDate(TestCase):
    # This will track possible changes to the list of GO terms
    URL = "https://current.geneontology.org/ontology/external2go/uniprotkb_sl2go"
    VERSION_DATE_REGEX = r"!version date:\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"

    def fetch_version_date(self):
        response = requests.get(self.URL)
        if response.status_code == 200:
            content = response.text
            match = re.search(self.VERSION_DATE_REGEX, content)
            if match:
                return match.group(1)
        return None

    def test_version_date_change(self):
        new_version_date = self.fetch_version_date()
        current_version_date = "2024/04/08 15:39:30"
        self.assertEqual(new_version_date, current_version_date)
