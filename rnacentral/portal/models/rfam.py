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

from .go_terms import OntologyTerm

RFAM_FAMILY_URL = "http://rfam.org/family/"


class RfamClan(models.Model):
    """
    A simple container to store information about Rfam clans. This is just to
    contain some useful meta data about clans for display in RNAcentral.
    """

    rfam_clan_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=1000)
    family_count = models.PositiveIntegerField()

    class Meta:
        db_table = "rfam_clans"
        ordering = ["rfam_clan_id"]

    def __str__(self):
        return self.name

    def url(self):
        return "http://rfam.org/clan/" + self.rfam_clan_id


class RfamModel(models.Model):
    """
    A simple container about Rfam families. This table contains just enough
    data to make it easy to display Rfam family data in RNAcentral.
    """

    rfam_model_id = models.CharField(max_length=20, primary_key=True)
    short_name = models.CharField(max_length=50)
    long_name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000, null=True)
    rfam_clan_id = models.ForeignKey(
        RfamClan,
        db_column="rfam_clan_id",
        to_field="rfam_clan_id",
        null=True,
        on_delete=models.CASCADE,
    )

    seed_count = models.PositiveIntegerField()
    full_count = models.PositiveIntegerField()
    length = models.PositiveIntegerField()
    is_suppressed = models.BooleanField(default=False)
    domain = models.CharField(max_length=50, null=True)
    rna_type = models.CharField(max_length=250)
    rfam_rna_type = models.TextField()

    class Meta:
        db_table = "rfam_models"
        ordering = ["rfam_model_id"]

    def __str__(self):
        return self.rfam_model_id

    @classmethod
    def url_of(cls, rfam_model_id):
        return RFAM_FAMILY_URL + rfam_model_id

    @property
    def url(self):
        return RFAM_FAMILY_URL + self.rfam_model_id

    @property
    def thumbnail_url(self):
        return "http://rfam.org/family/%s/thumbnail" % self.rfam_model_id

    def twod_url(self):
        return self.url + "#tabview=tab3"

    def go_terms(self):
        terms = []
        mapping = RfamGoTerm.objects.select_related("go_term").filter(
            rfam_model_id=self.rfam_model_id
        )
        for result in mapping.all():
            terms.append(result.go_term)

        return terms


class RfamHit(models.Model):
    """
    This represents a hit of an Rfam model against a particular sequence. The
    idea is that we represent the regions of the sequence and model that are
    matched.
    """

    rfam_hit_id = models.AutoField(primary_key=True)

    upi = models.ForeignKey(
        "Rna", db_column="upi", to_field="upi", on_delete=models.CASCADE
    )
    sequence_start = models.PositiveIntegerField()
    sequence_stop = models.PositiveIntegerField()
    sequence_completeness = models.FloatField()

    rfam_model = models.ForeignKey(
        RfamModel,
        db_column="rfam_model_id",
        to_field="rfam_model_id",
        on_delete=models.CASCADE,
    )
    model_start = models.PositiveIntegerField()
    model_stop = models.PositiveIntegerField()
    model_completeness = models.FloatField()

    overlap = models.CharField(max_length=30)
    e_value = models.FloatField()
    score = models.FloatField()

    class Meta:
        db_table = "rfam_model_hits"
        ordering = ["rfam_hit_id"]

    def __str__(self):
        return self.rfam_hit_id

    @property
    def rfam_clan_id(self):
        return self.rfam_model.rfam_clan_id


class RfamAnalyzedSequences(models.Model):
    """
    This table keeps track of all sequences which have been analyzed for Rfam
    families. This is useful for finding sequences which have no annotations
    (they will not have entries in rfam_hits, but will have entries here), or
    sequences that have not yet been run (will not show up here).
    """

    upi = models.ForeignKey(
        "Rna",
        db_column="upi",
        to_field="upi",
        primary_key=True,
        on_delete=models.CASCADE,
    )
    date = models.DateField()

    class Meta:
        db_table = "rfam_analyzed_sequences"
        ordering = ["date"]

    def __str__(self):
        return self.upi


class RfamGoTerm(models.Model):
    rfam_go_term_id = models.AutoField(primary_key=True)
    go_term = models.ForeignKey(
        OntologyTerm,
        db_column="ontology_term_id",
        to_field="ontology_term_id",
        related_name="go_term",
        on_delete=models.CASCADE,
    )
    rfam_model = models.ForeignKey(
        RfamModel,
        db_column="rfam_model_id",
        to_field="rfam_model_id",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "rfam_go_terms"
        ordering = ["rfam_go_term_id"]
        unique_together = (("rfam_model", "go_term"),)

    def __str__(self):
        return self.rfam_go_term_id
