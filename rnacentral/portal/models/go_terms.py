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
from jsonfield import JSONField  # Import from django-jsonfield package


class GoTerm(models.Model):
    """
    Gene Ontology terms.
    """
    go_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    definition = models.TextField()
    ontology = models.CharField(max_length=20)

    class Meta:
        db_table = 'go_terms'

    def __str__(self):
        return f"{self.go_id}: {self.name}"


class GoAnnotation(models.Model):
    """
    Gene Ontology annotations.
    """
    rna = models.ForeignKey('Rna', on_delete=models.CASCADE, db_column='upi')
    taxid = models.IntegerField()
    go_term = models.ForeignKey(GoTerm, on_delete=models.CASCADE, db_column='go_id')
    evidence_code = models.CharField(max_length=3)
    assigned_by = models.CharField(max_length=20)
    qualifier = models.CharField(max_length=20, null=True, blank=True)
    
    # Use JSONField from django-jsonfield instead of models.JSONField
    extensions = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'go_annotations'
        unique_together = ('rna', 'taxid', 'go_term', 'evidence_code', 'assigned_by', 'qualifier')

    def __str__(self):
        return f"{self.rna.upi}_{self.taxid} -> {self.go_term.go_id}"


class GoAnnotationSource(models.Model):
    """
    Sources for GO annotations.
    """
    source_id = models.CharField(max_length=50, primary_key=True)
    source_name = models.CharField(max_length=100)
    source_url = models.URLField(null=True, blank=True)

    class Meta:
        db_table = 'go_annotation_sources'

    def __str__(self):
        return self.source_name