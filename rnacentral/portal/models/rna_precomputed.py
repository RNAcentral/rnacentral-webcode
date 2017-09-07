from django.db import models


class RnaPrecomputed(models.Model):
    id = models.CharField(max_length=22, primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', to_field='upi', related_name='precomputed')
    taxid = models.IntegerField(db_index=True, null=True)
    description = models.CharField(max_length=250)
    rna_type = models.CharField(max_length=250)

    class Meta:
        db_table = 'rnc_rna_precomputed'