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

Quick reference:
CharField - regular model field
Field - model method call
SerializerMethodField - serializer method call
HyperlinkedIdentityField - link to a view

"""
import re

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Min, Max
from rest_framework import serializers
from rest_framework import pagination

from portal.models import Rna, Xref, Reference, Database, Accession, Release, Reference, Modification
from portal.models.reference_map import Reference_map
from portal.models.chemical_component import ChemicalComponent


class RawCitationSerializer(serializers.ModelSerializer):
    """Serializer class for literature citations. Used in conjunction with raw querysets."""
    authors = serializers.CharField(source='get_authors_list')
    publication = serializers.CharField(source='location')
    pubmed_id = serializers.CharField(source='pubmed')
    doi = serializers.CharField(source='doi')
    title = serializers.Field(source='get_title')
    pub_id = serializers.Field(source='id')

    class Meta:
        model = Reference
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi', 'pub_id')


class CitationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for literature citations."""
    authors = serializers.CharField(source='data.get_authors_list')
    publication = serializers.CharField(source='data.location')
    pubmed_id = serializers.CharField(source='data.pubmed')
    doi = serializers.CharField(source='data.doi')
    title = serializers.Field(source='data.get_title')
    pub_id = serializers.Field(source='data.id')

    class Meta:
        model = Reference_map
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi', 'pub_id')


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for individual cross-references."""
    id = serializers.CharField(source='accession')
    citations = serializers.HyperlinkedIdentityField(view_name='accession-citations')
    rna_type = serializers.Field(source='get_rna_type')
    expert_db_url = serializers.Field(source='get_expert_db_external_url')

    # database-specific fields
    pdb_entity_id = serializers.Field(source='get_pdb_entity_id')
    pdb_structured_note = serializers.Field(source='get_pdb_structured_note')
    hgnc_enembl_id = serializers.Field(source='get_hgnc_ensembl_id')
    hgnc_id = serializers.Field(source='get_hgnc_id')
    biotype = serializers.Field(source='get_biotype')
    rna_type = serializers.Field(source='get_rna_type')
    srpdb_id = serializers.Field(source='get_srpdb_id')
    ena_url = serializers.Field(source='get_ena_url')
    gencode_transcript_id = serializers.Field(source='get_gencode_transcript_id')
    gencode_ensembl_url = serializers.Field(source='get_gencode_ensembl_url')
    ensembl_species_url = serializers.Field(source='get_ensembl_species_url')

    class Meta:
        model = Accession
        fields = (
            'url', 'id', 'parent_ac', 'seq_version', 'description', 'external_id', 'optional_id',
            'species', 'rna_type', 'gene', 'product', 'organelle',
            'citations', 'expert_db_url',
            'pdb_entity_id', 'pdb_structured_note', 'hgnc_enembl_id', 'hgnc_id',
            'biotype', 'rna_type', 'srpdb_id', 'ena_url',
            'gencode_transcript_id',
            'gencode_ensembl_url', 'ensembl_species_url'
        )


class ChemicalComponentSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for chemical components."""
    id = serializers.CharField()
    description = serializers.CharField()
    one_letter_code = serializers.CharField()
    ccd_id = serializers.CharField()
    source = serializers.CharField()
    modomics_short_name = serializers.CharField()
    pdb_url = serializers.Field(source='get_pdb_url')
    modomics_url = serializers.Field(source='get_modomics_url')

    class Meta:
        model = ChemicalComponent


class ModificationSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for modified positions."""
    position = serializers.IntegerField()
    author_assigned_position = serializers.IntegerField()
    chem_comp = ChemicalComponentSerializer(source='modification_id')

    class Meta:
        model = Modification


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for all cross-references associated with an RNAcentral id."""
    database = serializers.CharField(source='db.display_name')
    is_expert_db = serializers.SerializerMethodField('is_expert_xref')
    is_active = serializers.Field('is_active')
    first_seen = serializers.CharField(source='created.release_date')
    last_seen = serializers.CharField(source='last.release_date')
    accession = AccessionSerializer()

    # database-specific fields
    modifications = ModificationSerializer(many=True)
    is_rfam_seed = serializers.Field(source='is_rfam_seed')
    ncbi_gene_id = serializers.Field(source='get_ncbi_gene_id')
    ndb_external_url = serializers.Field(source='get_ndb_external_url')
    mirbase_mature_products = serializers.SerializerMethodField('get_mirbase_mature_products')
    mirbase_precursor = serializers.SerializerMethodField('get_mirbase_precursor')
    refseq_mirna_mature_products = serializers.SerializerMethodField('get_refseq_mirna_mature_products')
    refseq_mirna_precursor = serializers.SerializerMethodField('get_refseq_mirna_precursor')
    refseq_splice_variants = serializers.SerializerMethodField('get_refseq_splice_variants')
    # tmrna_mate_upi = serializers.SerializerMethodField('get_tmrna_mate_upi')
    # tmrna_type = serializers.Field(source='get_tmrna_type')
    ensembl_division = serializers.Field(source='get_ensembl_division')
    ucsc_db_id = serializers.Field(source='get_ucsc_db_id')
    genomic_coordinates = serializers.SerializerMethodField('get_genomic_coordinates')

    # statistics on species

    class Meta:
        model = Xref
        fields = (
            'database', 'is_expert_db', 'is_active', 'first_seen', 'last_seen', 'taxid', 'accession',
            'modifications',  # used to send ~100 queries, optimized to 1
            'is_rfam_seed', 'ncbi_gene_id', 'ndb_external_url',
            'mirbase_mature_products', 'mirbase_precursor',
            'refseq_mirna_mature_products', 'refseq_mirna_precursor',
            'refseq_splice_variants',
            # 'tmrna_mate_upi',
            # 'tmrna_type',
            'ensembl_division', 'ucsc_db_id',  # 200-400 ms, no requests
            'genomic_coordinates'  # used to send ~100 queries, optimized down to 1
        )

    def is_expert_xref(self, obj):
        return True if obj.accession.non_coding_id else False

    def upis_to_urls(self, upis):
        protocol = 'https://' if self.context['request'].is_secure() else 'http://'
        hostport = self.context['request'].get_host()
        return [protocol + hostport + reverse('unique-rna-sequence', kwargs={'upi': upi}) for upi in upis]

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


class PaginatedXrefSerializer(pagination.PaginationSerializer):
    """Paginated version of XrefSerializer."""
    class Meta:
        object_serializer_class = XrefSerializer


class RnaListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rna
        fields = ('__all__')


class RnaNestedSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for a unique RNAcentral sequence."""
    sequence = serializers.Field(source='get_sequence')
    xrefs = serializers.HyperlinkedIdentityField(view_name='rna-xrefs')
    publications = serializers.HyperlinkedIdentityField(view_name='rna-publications')
    rnacentral_id = serializers.CharField(source='upi')
    is_active = serializers.Field(source='is_active')
    description = serializers.Field(source='get_description')
    rna_type = serializers.Field(source='get_rna_type')
    count_distinct_organisms = serializers.Field(source='count_distinct_organisms')
    distinct_databases = serializers.Field(source='get_distinct_database_names')

    class Meta:
        model = Rna
        fields = (
            'url', 'rnacentral_id', 'md5', 'sequence', 'length', 'xrefs',
            'publications', 'is_active', 'description', 'rna_type',
            'count_distinct_organisms', 'distinct_databases'
        )


class RnaSpeciesSpecificSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for species-specific RNAcentral ids.

    Requires context['xrefs'] and context['taxid'].
    """
    sequence = serializers.Field(source='get_sequence')
    rnacentral_id = serializers.SerializerMethodField('get_species_specific_id')
    description = serializers.SerializerMethodField('get_species_specific_description')
    species = serializers.SerializerMethodField('get_species_name')
    genes = serializers.SerializerMethodField('get_genes')
    ncrna_types = serializers.SerializerMethodField('get_ncrna_types')
    taxid = serializers.SerializerMethodField('get_taxid')
    is_active = serializers.SerializerMethodField('is_active_id')
    distinct_databases = serializers.SerializerMethodField('get_distinct_database_names')

    def is_active_id(self, obj):
        """Return false if all xrefs with this taxid are inactive."""
        return bool(self.context['xrefs'].filter(deleted='N').count())

    def get_species_specific_id(self, obj):
        """Return a species-specific id using the underscore (used by Protein2GO)."""
        return obj.upi + '_' + self.context['taxid']

    def get_species_specific_description(self, obj):
        """Get species-specific description of the RNA sequence."""
        return obj.get_description(self.context['taxid'])

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

    class Meta:
        model = Rna
        fields = ('rnacentral_id', 'sequence', 'length', 'description',
                  'species', 'taxid', 'genes', 'ncrna_types', 'is_active',
                  'distinct_databases')


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
        serializer = PaginatedXrefSerializer(xrefs, context=self.context)
        return serializer.data


class RnaFastaSerializer(serializers.ModelSerializer):
    """Serializer for presenting RNA sequences in FASTA format"""
    fasta = serializers.Field(source='get_sequence_fasta')

    class Meta:
        model = Rna
        fields = ('fasta',)


class RnaGffSerializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in GFF format"""
    gff = serializers.Field(source='get_gff')

    class Meta:
        model = Rna
        fields = ('gff',)


class RnaGff3Serializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in GFF format"""
    gff3 = serializers.Field(source='get_gff3')

    class Meta:
        model = Rna
        fields = ('gff3',)


class RnaBedSerializer(serializers.ModelSerializer):
    """Serializer for presenting genomic coordinates in UCSC BED format"""
    bed = serializers.Field(source='get_ucsc_bed')

    class Meta:
        model = Rna
        fields = ('bed',)
