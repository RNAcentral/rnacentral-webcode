from django.db import models


class Gene(models.Model):
    """ Gene details """
    id = models.AutoField(primary_key=True)
    name = models.TextField(db_column='public_name', blank=False, null=False)
    chromosome = models.CharField()
    start = models.IntegerField()
    stop = models.IntegerField()
    strand = models.CharField(max_length=1)

    class Meta:
        db_table = 'rnc_genes'
        verbose_name = 'Gene'
        verbose_name_plural = 'Genes'

    def __str__(self):
        return self.name