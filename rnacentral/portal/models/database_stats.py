from django.db import models


class DatabaseStats(models.Model):
    """
    These data are kept in a separate table because accessing CLOBs is slow,
    and this table will only be loaded when necessary.
    """
    database = models.CharField(max_length=30, primary_key=True)
    length_counts = models.TextField()
    taxonomic_lineage = models.TextField()

    class Meta:
        db_table = 'rnc_database_json_stats'