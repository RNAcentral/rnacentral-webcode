from django.db import models


class GoflowResults(models.Model):
    
    # IDs
    urs_taxid = models.TextField(help_text="URS taxonomic identifier")
    rna_id = models.TextField(help_text="RNA identifier")
    pmcid = models.TextField(help_text="PubMed Central ID", db_column="pmcid", primary_key=True)
    
    # Filters and flags
    mirna_binding_filter = models.BooleanField(default=False)
    mirna_cluster = models.BooleanField(default=False)
    binding_type_filter = models.BooleanField(default=False)
    experimental_evidence = models.BooleanField(default=False)
    functional_interaction = models.BooleanField(default=False)
    mirna_mrna_binding = models.BooleanField(default=False)
    effect_endogenous_2 = models.BooleanField(default=False)
    computational_prediction = models.BooleanField(default=False)
    effect_endogenous_3 = models.BooleanField(default=False)
    mirna_changes = models.BooleanField(default=False)
    no_annotation = models.BooleanField(default=False)
    validated_binding_only = models.BooleanField(default=False)
    validated_binding_mrna = models.BooleanField(default=False)
    validated_binding_translation = models.BooleanField(default=False)
    no_validated_binding = models.BooleanField(default=False)
    mrna_expression_assay = models.BooleanField(default=False)
    
    # Results
    mirna_binding_filter_result = models.TextField(blank=True, null=True)
    mirna_cluster_result = models.TextField(blank=True, null=True)
    binding_type_filter_result = models.TextField(blank=True, null=True)
    experimental_evidence_result = models.BooleanField(default=False)
    functional_interaction_result = models.BooleanField(default=False)
    mirna_mrna_binding_result = models.BooleanField(default=False)
    effect_endogenous_2_result = models.BooleanField(default=False)
    computational_prediction_result = models.BooleanField(default=False)
    effect_endogenous_3_result = models.BooleanField(default=False)
    mirna_changes_result = models.BooleanField(default=False)
    no_annotation_result = models.TextField(blank=True, null=True)
    validated_binding_only_result = models.TextField(blank=True, null=True)
    validated_binding_mrna_result = models.TextField(blank=True, null=True)
    validated_binding_translation_result = models.TextField(blank=True, null=True)
    no_validated_binding_result = models.TextField(blank=True, null=True)
    mrna_expression_assay_result = models.BooleanField(default=False)
    
    # Evidence
    mirna_binding_filter_evidence = models.TextField(blank=True, null=True)
    mirna_binding_filter_reasoning = models.TextField(blank=True, null=True)
    mirna_cluster_evidence = models.TextField(blank=True, null=True)
    mirna_cluster_reasoning = models.TextField(blank=True, null=True)
    binding_type_filter_evidence = models.TextField(blank=True, null=True)
    binding_type_filter_reasoning = models.TextField(blank=True, null=True)
    experimental_evidence_evidence = models.TextField(blank=True, null=True)
    experimental_evidence_reasoning = models.TextField(blank=True, null=True)
    functional_interaction_evidence = models.TextField(blank=True, null=True)
    functional_interaction_reasoning = models.TextField(blank=True, null=True)
    mrna_expression_assay_evidence = models.TextField(blank=True, null=True)
    mrna_expression_assay_reasoning = models.TextField(blank=True, null=True)
    mirna_changes_evidence = models.TextField(blank=True, null=True)
    mirna_changes_reasoning = models.TextField(blank=True, null=True)
    validated_binding_mrna_evidence = models.TextField(blank=True, null=True)
    validated_binding_mrna_reasoning = models.TextField(blank=True, null=True)
    no_annotation_evidence = models.TextField(blank=True, null=True)
    no_annotation_reasoning = models.TextField(blank=True, null=True)
    mirna_mrna_binding_evidence = models.TextField(blank=True, null=True)
    mirna_mrna_binding_reasoning = models.TextField(blank=True, null=True)
    computational_prediction_evidence = models.TextField(blank=True, null=True)
    computational_prediction_reasoning = models.TextField(blank=True, null=True)
    effect_endogenous_3_evidence = models.TextField(blank=True, null=True)
    effect_endogenous_3_reasoning = models.TextField(blank=True, null=True)
    validated_binding_only_evidence = models.TextField(blank=True, null=True)
    validated_binding_only_reasoning = models.TextField(blank=True, null=True)
    no_validated_binding_evidence = models.TextField(blank=True, null=True)
    no_validated_binding_reasoning = models.TextField(blank=True, null=True)
    validated_binding_translation_evidence = models.TextField(blank=True, null=True)
    validated_binding_translation_reasoning = models.TextField(blank=True, null=True)
    effect_endogenous_2_evidence = models.TextField(blank=True, null=True)
    effect_endogenous_2_reasoning = models.TextField(blank=True, null=True)
    
    # Annotation and targets
    annotation = models.TextField(blank=True, null=True)
    target_0 = models.TextField(blank=True, null=True)
    target_1 = models.TextField(blank=True, null=True)
    target_2 = models.TextField(blank=True, null=True)
    target_3 = models.TextField(blank=True, null=True)
    target_4 = models.TextField(blank=True, null=True)
    target_5 = models.TextField(blank=True, null=True)
    target_6 = models.TextField(blank=True, null=True)
    target_7 = models.TextField(blank=True, null=True)
    target = models.TextField(blank=True, null=True)
    targets = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'go_flow_llm_curation_results'
        verbose_name = 'GoFlow Curation Results'
        verbose_name_plural = 'GoFlow Curation Results'
    
    def __str__(self):
        return f"GoFlow Results: {self.rna_id} - {self.urs_taxid}"
    
    def get_target_list(self):
        """
        Returns a list of non-empty target fields.
        """
        targets = []
        for i in range(8):
            target_value = getattr(self, f'target_{i}', None)
            if target_value:
                targets.append(target_value)
        return targets
    
    def has_experimental_evidence(self):
        """
        Returns True if there is any experimental evidence for this binding.
        """
        return (self.experimental_evidence or 
                self.functional_interaction or 
                self.validated_binding_mrna or 
                self.validated_binding_translation)
    
    def has_computational_evidence(self):
        """
        Returns True if there is computational prediction evidence.
        """
        return self.computational_prediction