from django.db import models
from . import (
    OntologyTerm,
    SequenceRegion,
    RnaPrecomputed
    )  

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


class GeneMember(models.Model):
    """ Connecting genes to sequence regions"""
    id = models.AutoField(primary_key=True)
    rnc_gene = models.ForeignKey(
        Gene, 
        on_delete=models.CASCADE, 
        related_name='gene_members',
        db_column='rnc_gene_id'
    )
    locus_id = models.IntegerField()  # References rnc_sequence_regions.id
    
    class Meta:
        db_table = 'rnc_gene_members'
        verbose_name = 'Gene Member'
        verbose_name_plural = 'Gene Members'
        indexes = [
            models.Index(fields=['rnc_gene_id', 'locus_id']),
        ]
    
    def __str__(self):
        return f"Gene {self.rnc_gene.name} -> Locus {self.locus_id}"
    
    @property
    def sequence_region(self):
        """Get the related SequenceRegion """
        try:
            return SequenceRegion.objects.get(id=self.locus_id)
        except SequenceRegion.DoesNotExist:
            return None
    
    @property
    def rna_precomputed(self):
        """Get the related RnaPrecomputed """
        sequence_region = self.sequence_region
        if sequence_region:
            try:
                return RnaPrecomputed.objects.get(id=sequence_region.urs_taxid)
            except RnaPrecomputed.DoesNotExist:
                return None
        return None