from django.db import models


class GenomicCoordinates(models.Model):
    accession = models.ForeignKey('Accession', db_column='accession', to_field='accession', related_name='coordinates')
    primary_accession = models.CharField(max_length=50)
    local_start = models.IntegerField()  # start relative to ENA accession
    local_end = models.IntegerField()  # stop relative to ENA accession
    chromosome = models.CharField(max_length=50, db_column='name')
    primary_start = models.IntegerField()  # relative to chromosome (which is a chromosome or other top level genome id)
    primary_end = models.IntegerField()  # relative to chromosome (which is a chromosome or other top level genome id)
    strand = models.IntegerField()

    class Meta:
        db_table = 'rnc_coordinates'