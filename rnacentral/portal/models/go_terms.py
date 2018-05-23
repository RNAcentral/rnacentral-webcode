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
from django.contrib.postgres.fields import JSONField


class OntologyTerm(models.Model):
    # An ontology term id is of the form: GO:0006617
    ontology_term_id = models.CharField(
        max_length=10,
        db_index=True,
        primary_key=True
    )
    ontology = models.CharField(max_length=5)
    name = models.TextField()
    definition = models.TextField()

    class Meta:
        db_table = 'ontology_terms'

    def url(self):
        if self.ontology != 'GO':
            return None
        return 'http://amigo.geneontology.org/amigo/term/%s' % self.ontology_term_id

    def quickgo_url(self):
        if self.ontology != 'GO':
            return None
        return 'https://www.ebi.ac.uk/QuickGO/term/%s' % self.ontology_term_id


class GoAnnotation(models.Model):
    go_term_annotation_id = models.AutoField(primary_key=True)
    rna_id = models.CharField(max_length=50, null=False)
    qualifier = models.CharField(max_length=30, null=False)
    ontology_term = models.ForeignKey(
        'OntologyTerm',
        db_column='ontology_term_id',
        to_field='ontology_term_id',
        null=False,
        related_name='go_annotations',
    )
    evidence_code = models.ForeignKey(
        'OntologyTerm',
        db_column='evidence_code',
        to_field='ontology_term_id',
        null=False,
        related_name='go_annotation_evidence',
    )
    assigned_by = models.CharField(max_length=50)
    extensions = JSONField()

    class Meta:
        db_table = 'go_term_annotations'
