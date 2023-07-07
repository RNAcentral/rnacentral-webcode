from django.contrib.postgres.fields import JSONField
from django.db import models


class Interactions(models.Model):
    id = models.AutoField(primary_key=True)
    intact_id = models.CharField(max_length=255, unique=True)
    urs_taxid = models.ForeignKey(
        "RnaPrecomputed",
        db_column="urs_taxid",
        related_name="urs_taxid_precomputed",
        on_delete=models.CASCADE,
    )
    interacting_id = models.CharField(max_length=255)
    names = JSONField()
    taxid = models.IntegerField()

    class Meta:
        db_table = "rnc_interactions"
        ordering = ["interacting_id"]

    def __str__(self):
        return self.intact_id
