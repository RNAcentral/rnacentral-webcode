from django.db import models


class Interactions(models.Model):
    id = models.AutoField(primary_key=True)
    intact_id = models.CharField(max_length=255, unique=True)
    urs_taxid = models.ForeignKey(
        "RnaPrecomputed",
        db_column="urs_taxid",
        related_name="urs_taxid_precomputed",
        on_delete=models.CASCADE,
        db_index=True
    )
    interacting_id = models.CharField(max_length=255, db_index=True)
    names = models.JSONField()
    taxid = models.IntegerField()

    class Meta:
        db_table = "rnc_interactions"
        ordering = ["interacting_id"]
        indexes = [
            models.Index(fields=['urs_taxid', 'interacting_id']),
        ]

    def __str__(self):
        return self.intact_id
