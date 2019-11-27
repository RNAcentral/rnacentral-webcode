"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import json

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Min, Max
from rest_framework import serializers

from portal.models import Rna, Xref, Reference,  Reference_map, ChemicalComponent, Database, DatabaseStats, Accession, \
    Release, Reference, Modification, RfamHit, RfamModel, RfamClan, RfamGoTerm, OntologyTerm, SequenceFeature, \
    EnsemblAssembly, EnsemblInsdcMapping, EnsemblKaryotype, GenomeMapping, \
    ProteinInfo, EnsemblCompara, RnaPrecomputed, SequenceRegion, SecondaryStructureWithLayout


class RawPublicationSerializer(serializers.ModelSerializer):
    """Serializer class for literature citations. Used in conjunction with raw querysets."""
    authors = serializers.ListField(serializers.CharField(), source='get_authors_list')
    publication = serializers.CharField(source='location')
    pubmed_id = serializers.CharField(source='pubmed')
    doi = serializers.CharField()
    title = serializers.CharField(source='get_title')
    pub_id = serializers.CharField(source='id')
    expert_db = serializers.BooleanField()

    class Meta:
        model = Reference
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi', 'pub_id', 'expert_db')


class CitationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for literature citations."""
    authors = serializers.ListField(serializers.CharField(), source='data.get_authors_list')
    publication = serializers.CharField(source='data.location')
    pubmed_id = serializers.CharField(source='data.pubmed')
    doi = serializers.CharField(source='data.doi')
    title = serializers.ReadOnlyField(source='data.get_title')
    pub_id = serializers.ReadOnlyField(source='data.id')

    class Meta:
        model = Reference_map
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi', 'pub_id')


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for individual cross-references."""
    id = serializers.CharField(source='accession')
    citations = serializers.HyperlinkedIdentityField(view_name='accession-citations')
    expert_db_url = serializers.ReadOnlyField(source='get_expert_db_external_url')

    # database-specific fields
    pdb_entity_id = serializers.ReadOnlyField(source='get_pdb_entity_id')
    pdb_structured_note = serializers.ReadOnlyField(source='get_pdb_structured_note')
    hgnc_enembl_id = serializers.ReadOnlyField(source='get_hgnc_ensembl_id')
    hgnc_id = serializers.ReadOnlyField(source='get_hgnc_id')
    biotype = serializers.ReadOnlyField(source='get_biotype')
    rna_type = serializers.ReadOnlyField(source='get_rna_type')
    srpdb_id = serializers.ReadOnlyField(source='get_srpdb_id')
    ena_url = serializers.ReadOnlyField(source='get_ena_url')
    ensembl_species_url = serializers.ReadOnlyField(source='get_ensembl_species_url')

    class Meta:
        model = Accession
        fields = (
            'url', 'id', 'parent_ac', 'seq_version', 'feature_start', 'feature_end', 'feature_name',
            'description', 'external_id', 'optional_id', 'locus_tag',
            'species', 'inference', 'rna_type', 'gene', 'product', 'organelle',
            'citations', 'expert_db_url', 'standard_name',
            'pdb_entity_id', 'pdb_structured_note', 'hgnc_enembl_id', 'hgnc_id',
            'biotype', 'rna_type', 'srpdb_id', 'ena_url',
            'ensembl_species_url'
        )


class ChemicalComponentSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for chemical components."""
    id = serializers.CharField()
    description = serializers.CharField()
    one_letter_code = serializers.CharField()
    ccd_id = serializers.CharField()
    source = serializers.CharField()
    modomics_short_name = serializers.CharField()
    pdb_url = serializers.ReadOnlyField(source='get_pdb_url')
    modomics_url = serializers.ReadOnlyField(source='get_modomics_url')

    class Meta:
        model = ChemicalComponent
        fields = (
            'id', 'description', 'one_letter_code', 'ccd_id', 'source', 'modomics_short_name', 'pdb_url', 'modomics_url'
        )


class ModificationSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for modified positions."""
    position = serializers.IntegerField()
    author_assigned_position = serializers.IntegerField()
    chem_comp = ChemicalComponentSerializer(source='modification_id')

    class Meta:
        model = Modification
        fields = ('position', 'author_assigned_position', 'chem_comp')


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for all cross-references associated with an RNAcentral id."""
    database = serializers.CharField(source='db.display_name')
    is_active = serializers.BooleanField(read_only=True)
    first_seen = serializers.CharField(source='created.release_date')
    last_seen = serializers.CharField(source='last.release_date')
    accession = AccessionSerializer()

    # database-specific fields
    modifications = ModificationSerializer(many=True)
    is_rfam_seed = serializers.BooleanField(read_only=True)
    ncbi_gene_id = serializers.CharField(source='get_ncbi_gene_id', read_only=True)
    ndb_external_url = serializers.URLField(source='get_ndb_external_url', read_only=True)
    mirbase_mature_products = serializers.SerializerMethodField()
    mirbase_precursor = serializers.SerializerMethodField()
    refseq_mirna_mature_products = serializers.SerializerMethodField()
    refseq_mirna_precursor = serializers.SerializerMethodField()
    refseq_splice_variants = serializers.SerializerMethodField()
    ensembl_splice_variants = serializers.SerializerMethodField()
    # tmrna_mate_upi = serializers.SerializerMethodField('get_tmrna_mate_upi')
    # tmrna_type = serializers.ReadOnlyField(source='get_tmrna_type')
    gencode_transcript_id = serializers.CharField(source='get_gencode_transcript_id', read_only=True)
    gencode_ensembl_url = serializers.CharField(source='get_gencode_ensembl_url', read_only=True)
    ensembl_division = serializers.DictField(source='get_ensembl_division', read_only=True)
    ucsc_db_id = serializers.CharField(source='get_ucsc_db_id', read_only=True)
    genomic_coordinates = serializers.SerializerMethodField()

    # statistics on species

    class Meta:
        model = Xref
        fields = (
            'database', 'is_active', 'first_seen', 'last_seen', 'taxid', 'accession',
            'modifications',  # used to send ~100 queries, optimized to 1
            'is_rfam_seed', 'ncbi_gene_id', 'ndb_external_url',
            'mirbase_mature_products', 'mirbase_precursor',
            'refseq_mirna_mature_products', 'refseq_mirna_precursor',
            'refseq_splice_variants', 'ensembl_splice_variants',
            # 'tmrna_mate_upi',
            # 'tmrna_type',
            'gencode_transcript_id', 'gencode_ensembl_url',
            'ensembl_division', 'ucsc_db_id',  # 200-400 ms, no requests
            'genomic_coordinates'  # used to send ~100 queries, optimized down to 1
        )

    def upis_to_urls(self, upis):
        """
        Returns a list of urls or single url that points to unique rna sequence
        page, corresponding to given upi.

        :param upis: list of upis or a single upi
        :return: list of urls or a single url
        """
        protocol = 'https://' if self.context['request'].is_secure() else 'http://'
        hostport = self.context['request'].get_host()
        if isinstance(upis, list):
            return [protocol + hostport + reverse('unique-rna-sequence', kwargs={'upi': upi}) for upi in upis]
        else:  # upis is just a single item
            return protocol + hostport + reverse('unique-rna-sequence', kwargs={'upi': upis})

    def get_mirbase_mature_products(self, obj):
        return self.upis_to_urls(obj.mirbase_mature_products) if hasattr(obj, "mirbase_mature_products") else None

    def get_mirbase_precursor(self, obj):
        return self.upis_to_urls(obj.mirbase_precursor) if hasattr(obj, "mirbase_precursor") else None

    def get_refseq_mirna_mature_products(self, obj):
        return self.upis_to_urls(obj.refseq_mirna_mature_products) if hasattr(obj, "refseq_mirna_mature_products") else None

    def get_refseq_mirna_precursor(self, obj):
        return self.upis_to_urls(obj.refseq_mirna_precursor) if hasattr(obj, "refseq_mirna_precursor") else None

    def get_refseq_splice_variants(self, obj):
        return self.upis_to_urls(obj.refseq_splice_variants) if hasattr(obj, "refseq_splice_variants") else None

    def get_ensembl_splice_variants(self, obj):
        return self.upis_to_urls(obj.ensembl_splice_variants) if hasattr(obj, "ensembl_splice_variants") else None

    def get_tmrna_mate_upi(self, obj):
        return self.upis_to_urls(obj.tmrna_mate_upi) if hasattr(obj, "tmrna_mate_upi") else None

    def get_genomic_coordinates(self, obj):
        """Mirror the existing API while using the new GenomicCoordinates model."""

        # In Django1.9+ we could try removing obj.accession.coordinates.exists() check and
        # replace obj.accession.coordinates.all()[0] with obj.accession.coordinates.first(),
        # but currently this prevents re-use of related queryset and created N+1 requests:
        #
        #  first_coordinate = obj.accession.coordinates.all().first()
        #  if first_coordinate:
        #      data = {
        #          'chromosome': first_coordinate.chromosome,
        #          'strand': first_coordinate.strand
        #      }
        #      return data

        # TODO: bring back all() -> filter(chromosome__isnull=False), when postgres is fully populated

        if obj.accession.coordinates.exists() and obj.accession.coordinates.all()[0].chromosome:
            data = {
                'chromosome': obj.accession.coordinates.all()[0].chromosome,
                'strand': obj.accession.coordinates.all()[0].strand,
                'start': obj.accession.coordinates.all().aggregate(Min('primary_start'))['primary_start__min'],
                'end': obj.accession.coordinates.all().aggregate(Max('primary_end'))['primary_end__max']
            }

            exceptions = ['X', 'Y']
            if re.match(r'\d+', data['chromosome']) or data['chromosome'] in exceptions:
                data['ucsc_chromosome'] = 'chr' + data['chromosome']
            else:
                data['ucsc_chromosome'] = data['chromosome']
            return data


class RnaNestedSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for a unique RNAcentral sequence."""
    sequence = serializers.CharField(source='get_sequence', read_only=True)
    xrefs = serializers.HyperlinkedIdentityField(view_name='rna-xrefs')
    publications = serializers.HyperlinkedIdentityField(view_name='rna-publications')
    rnacentral_id = serializers.CharField(source='upi')
    is_active = serializers.BooleanField(read_only=True)
    description = serializers.CharField(source='get_description', read_only=True)
    rna_type = serializers.CharField(source='get_rna_type', read_only=True)
    count_distinct_organisms = serializers.IntegerField(read_only=True)
    distinct_databases = serializers.ReadOnlyField(source='get_distinct_database_names')

    class Meta:
        model = Rna
        fields = (
            'url', 'rnacentral_id', 'md5', 'sequence', 'length', 'xrefs',
            'publications', 'is_active', 'description', 'rna_type',
            'count_distinct_organisms', 'distinct_databases'
        )


class RnaSecondaryStructureSerializer(serializers.ModelSerializer):
    """Serializer for presenting RNA secondary structures"""
    data = serializers.SerializerMethodField('get_secondary_structures')

    class Meta:
        model = Rna
        fields = ('data', )

    def get_secondary_structures(self, obj):
        """Return secondary structures filtered by taxid."""
        return obj.get_secondary_structures(taxid=self.context['taxid'])


class SecondaryStructureSVGImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryStructureWithLayout
        fields = ('layout',)


class RnaSpeciesSpecificSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for species-specific RNAcentral ids.

    Requires context['xrefs'] and context['taxid'].
    """
    sequence = serializers.CharField(source='get_sequence', read_only=True)
    rnacentral_id = serializers.SerializerMethodField('get_species_specific_id')
    description = serializers.SerializerMethodField('get_species_specific_description')
    short_description = serializers.SerializerMethodField('get_short_description_name')
    species = serializers.SerializerMethodField('get_species_name')
    genes = serializers.SerializerMethodField()
    ncrna_types = serializers.SerializerMethodField()
    taxid = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField('is_active_id')
    distinct_databases = serializers.SerializerMethodField('get_distinct_database_names')

    class Meta:
        model = Rna
        fields = ('rnacentral_id', 'sequence', 'length', 'description', 'short_description',
                  'species', 'taxid', 'genes', 'ncrna_types', 'is_active',
                  'distinct_databases')

    def is_active_id(self, obj):
        """Return false if all xrefs with this taxid are inactive."""
        return bool(self.context['xrefs'].filter(deleted='N').count())

    def get_species_specific_id(self, obj):
        """Return a species-specific id using the underscore (used by Protein2GO)."""
        return obj.upi + '_' + self.context['taxid']

    def get_species_specific_description(self, obj):
        """Get species-specific description of the RNA sequence."""
        return obj.get_description(self.context['taxid'])

    def get_short_description_name(self, obj):
        """Get description without species name"""
        return obj.get_short_description(self.context['taxid'])

    def get_species_name(self, obj):
        """Get the name of the species based on taxid."""
        return self.context['xrefs'].first().accession.species

    def get_genes(self, obj):
        """Get a species-specific list of genes associated with the sequence in this particular sequence."""
        return self.context['xrefs'].values_list('accession__gene', flat=True)\
                                    .filter(accession__gene__isnull=False)\
                                    .distinct()

    def get_ncrna_types(self, obj):
        """
        Get a combined list of ncRNA types from the feature names
        and expand ncRNA feature type using ncRNA class info.
        """
        xrefs = self.context['xrefs']
        feature_names = xrefs.values_list('accession__feature_name', flat=True).distinct()

        if 'ncRNA' in feature_names:
            ncrna_classes = xrefs.values_list('accession__ncrna_class', flat=True)\
                                 .filter(accession__ncrna_class__isnull=False)\
                                 .distinct()
            ncrna_types = set(list(feature_names) + list(ncrna_classes))
            ncrna_types.discard('ncRNA')
        else:
            ncrna_types = list(feature_names)
        return ncrna_types

    def get_taxid(self, obj):
        return int(self.context['taxid'])

    def get_distinct_database_names(self, obj):
        return obj.get_distinct_database_names(taxid=self.get_taxid(obj))


class RnaFlatSerializer(RnaNestedSerializer):
    """Override the xrefs field in the default nested serializer to provide a flat representation."""
    xrefs = serializers.SerializerMethodField('paginated_xrefs')

    def paginated_xrefs(self, obj):
        """Include paginated xrefs."""
        queryset = obj.xrefs.all()
        page = self.context.get('page', 1)
        page_size = self.context.get('page_size', 100)
        paginator = Paginator(queryset, page_size)
        xrefs = paginator.page(page)

        serializer = XrefSerializer(xrefs, many=True, context=self.context)

        return serializer.data

    class Meta:
        model = Rna
        fields = (
            'url', 'rnacentral_id', 'md5', 'sequence', 'length', 'xrefs', 'publications',
            'is_active', 'description', 'rna_type',
            'count_distinct_organisms', 'distinct_databases'
        )


class RnaFastaSerializer(serializers.ModelSerializer):
    """Serializer for presenting RNA sequences in FASTA format"""
    fasta = serializers.CharField(source='get_sequence_fasta', read_only=True)

    class Meta:
        model = Rna
        fields = ('fasta',)


class ProteinTargetsSerializer(serializers.ModelSerializer):
    target_accession = serializers.CharField()  # use non-null target_accession instead of nullable protein_accession
    source_accession = serializers.CharField()
    methods = serializers.ListField(serializers.CharField())

    class Meta:
        model = ProteinInfo
        fields = ('target_accession', 'source_accession', 'description', 'label', 'synonyms', 'methods')


class LncrnaTargetsSerializer(serializers.ModelSerializer):
    target_accession = serializers.CharField()
    source_accession = serializers.CharField()
    target_urs_taxid = serializers.CharField()
    methods = serializers.ListField(serializers.CharField())
    description = serializers.SerializerMethodField('select_description')

    def select_description(self, obj):
        if hasattr(obj, 'target_rna_description'):
            return obj.target_rna_description
        elif hasattr(obj, 'target_ensembl_description'):
            return obj.target_ensembl_description
        else:
            return ''

    class Meta:
        model = ProteinInfo
        fields = ('target_accession', 'source_accession', 'description', 'label', 'synonyms', 'methods', 'description', 'target_urs_taxid')


class RnaGffSerializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in GFF format"""
    gff = serializers.CharField(source='get_gff', read_only=True)

    class Meta:
        model = Rna
        fields = ('gff',)


class RnaGff3Serializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in GFF format"""
    gff3 = serializers.CharField(source='get_gff3', read_only=True)

    class Meta:
        model = Rna
        fields = ('gff3',)


class RnaBedSerializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in UCSC BED format"""
    bed = serializers.CharField(source='get_ucsc_bed', read_only=True)

    class Meta:
        model = Rna
        fields = ('bed',)


class ExpertDatabaseStatsSerializer(serializers.ModelSerializer):
    """Serializer for presenting DatabaseStats"""
    length_counts = serializers.SerializerMethodField()
    taxonomic_lineage = serializers.SerializerMethodField()

    class Meta:
        model = DatabaseStats
        fields = ('database', 'length_counts', 'taxonomic_lineage')

    def get_length_counts(self, obj):
        return json.loads(obj.length_counts)

    def get_taxonomic_lineage(self, obj):
        return json.loads(obj.taxonomic_lineage)


class OntologyTermSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)
    quickgo_url = serializers.CharField(read_only=True)

    class Meta:
        model = OntologyTerm
        fields = ('ontology_term_id', 'ontology', 'name', 'definition', 'url', 'quickgo_url')


class RfamClanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfamClan
        fields = ('rfam_clan_id', 'name', 'description', 'family_count')


class RfamModelSerializer(serializers.ModelSerializer):
    rfam_clan = RfamClanSerializer(source='rfam_clan_id')
    go_terms = OntologyTermSerializer(many=True)

    class Meta:
        model = RfamModel
        fields = ('rfam_model_id', 'short_name', 'long_name', 'description', 'rfam_clan',
                  'seed_count', 'full_count', 'length', 'is_suppressed', 'domain', 'rna_type',
                  'rfam_rna_type', 'thumbnail_url', 'url', 'go_terms')


class RfamHitSerializer(serializers.ModelSerializer):
    rfam_model = RfamModelSerializer()
    rfam_status = serializers.SerializerMethodField()

    class Meta:
        model = RfamHit
        fields = ('sequence_start', 'sequence_stop', 'sequence_completeness', 'rfam_model', 'rfam_status')

    def get_rfam_status(self, obj):
        if 'taxid' in self.context:
            return json.loads(obj.upi.get_rfam_status(self.context['taxid']).as_json())
        else:
            return json.loads(obj.upi.get_rfam_status().as_json())


class SequenceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceFeature
        fields = '__all__'


class EnsemblAssemblySerializer(serializers.ModelSerializer):
    human_readable_ensembl_url = serializers.SerializerMethodField()
    example_chromosome = serializers.SerializerMethodField()
    example_start = serializers.SerializerMethodField()
    example_end = serializers.SerializerMethodField()

    class Meta:
        model = EnsemblAssembly
        fields = ('assembly_id', 'assembly_full_name', 'gca_accession', 'assembly_ucsc',
                  'common_name', 'taxid', 'ensembl_url', 'human_readable_ensembl_url', 'division', 'subdomain',
                  'example_chromosome', 'example_start', 'example_end')

    def get_human_readable_ensembl_url(self, obj):
        return obj.ensembl_url.replace("_", " ").capitalize()

    def get_example_chromosome(self, obj):
        return obj.example_chromosome

    def get_example_start(self, obj):
        return obj.example_start

    def get_example_end(self, obj):
        return obj.example_end


class EnsemblInsdcMappingSerializer(serializers.ModelSerializer):
    assembly = EnsemblAssemblySerializer(source='assembly_id')

    class Meta:
        model = EnsemblInsdcMapping
        fields = ('insdc', 'ensembl_name', 'assembly')


class EnsemblKaryotypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnsemblKaryotype
        fields = ('karyotype', )


class RnaPrecomputedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RnaPrecomputed
        fields = ('id', 'rna_type', 'description', 'databases')


class EnsemblComparaSerializer(serializers.ModelSerializer):
    rnacentral_id = RnaPrecomputedSerializer(source='urs_taxid')

    class Meta:
        model = EnsemblCompara
        fields = ('ensembl_transcript_id', 'rnacentral_id')


class RnaPrecomputedJsonSerializer(serializers.ModelSerializer):
    """Serializer class for the Json download."""
    sequence = serializers.CharField(source='get_sequence', read_only=True)

    class Meta:
        model = RnaPrecomputed
        fields = (
            'id', 'rna_type', 'description', 'databases', 'sequence'
        )
