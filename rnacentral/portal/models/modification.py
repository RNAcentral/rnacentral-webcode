from caching.base import CachingMixin, CachingManager
from django.db import models


class Modification(CachingMixin, models.Model):
    """Describe modified nucleotides at certain sequence positions reported in xrefs."""
    id = models.AutoField(primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', related_name='modifications')
    xref = models.ForeignKey('Xref', db_column='accession', to_field='accession', related_name='modifications')
    position = models.PositiveIntegerField()  # absolute sequence position, always > 0
    author_assigned_position = models.IntegerField()  # can be negative, e.g. 3I2S chain A
    modification_id = models.ForeignKey('ChemicalComponent', db_column='modification_id')

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_modifications'