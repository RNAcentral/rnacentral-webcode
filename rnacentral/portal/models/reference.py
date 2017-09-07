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

from django.db import models


class Reference(models.Model):
    authors = models.TextField()
    location = models.CharField(max_length=4000)
    title = models.CharField(max_length=4000)
    pubmed = models.CharField(max_length=10, db_column='pmid')
    doi = models.CharField(max_length=80)

    def get_title(self):
        title = self.title
        if self.location[:9] == 'Submitted':
            title = 'INSDC submission'
        else:
            title = title if title else 'No title available'
        return title

    def get_authors_list(self):
        """Get publication authors as a list."""
        return self.authors.split(', ') if self.authors else []

    class Meta:
        db_table = 'rnc_references'