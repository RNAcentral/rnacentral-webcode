# -*- coding: utf-8 -*-

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


class GoTerm(models.Model):
    # A GO term id is of the form: GO:0006617
    go_term_id = models.CharField(
        max_length=10,
        db_index=True,
        primary_key=True
    )
    name = models.TextField()

    class Meta:
        db_table = 'go_terms'

    def url(self):
        return 'http://amigo.geneontology.org/amigo/term/%s' % self.go_term_id

    def quickgo_url(self):
        return 'https://www.ebi.ac.uk/QuickGO/term/%s' % self.go_term_id
