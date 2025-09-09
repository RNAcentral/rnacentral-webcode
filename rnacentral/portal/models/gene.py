from django.db import models
from . import OntologyTerm  

class Gene(models.Model):
    """ Gene details """
    id = models.AutoField(primary_key=True)
    name = models.TextField(db_column='public_name')
    chromosome = models.CharField(max_length=40)
    start = models.IntegerField()
    stop = models.IntegerField()
    strand = models.CharField(max_length=1)

    class Meta:
        db_table = 'rnc_genes'
        verbose_name = 'Gene'
        verbose_name_plural = 'Genes'

    def __str__(self):
        return self.name

class GeneMetadata(models.Model):
    """ Gene Metadata """
    id = models.AutoField(primary_key=True, db_column='rnc_gene_metadata_id')
    gene = models.OneToOneField(Gene, on_delete=models.CASCADE, related_name='metadata', db_column='rnc_gene_id')
    description = models.TextField()
    short_description = models.TextField()
    ontology_term = models.ForeignKey(
        OntologyTerm,  
        on_delete=models.CASCADE,
        to_field='ontology_term_id',
        db_column='so_rna_type',
        related_name='gene_metadata'
    )

    def __str__(self):
        return self.description
    
    class Meta:
        db_table = 'rnc_gene_metadata'