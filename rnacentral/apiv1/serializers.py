"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

from portal.models import Rna, Xref, Reference, Database, Accession, Release, Reference, Reference_map
from rest_framework import serializers


class CitationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for literature citations.
    """
    authors = serializers.CharField(source='data.authors')
    publication = serializers.CharField(source='data.location')
    pubmed_id = serializers.CharField(source='data.pubmed')
    doi = serializers.CharField(source='data.doi')
    title = serializers.Field(source='data.get_title')
    pub_id = serializers.Field(source='data.id')

    class Meta:
        model = Reference_map
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi', 'pub_id')


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for individual cross-references.
    """
    id = serializers.CharField(source='accession')
    citations = serializers.HyperlinkedIdentityField(view_name='accession-citations')
    source_url = serializers.Field(source='get_ena_url')
    rna_type = serializers.Field(source='get_rna_type')
    expert_db_url = serializers.Field(source='get_expert_db_external_url')

    class Meta:
        model = Accession
        fields = ('url', 'id', 'description', 'external_id', 'optional_id',
                  'species', 'rna_type', 'gene', 'product', 'organelle',
                  'citations', 'source_url', 'expert_db_url')


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for all cross-references associated with an RNAcentral id.
    """
    database = serializers.CharField(source='db.display_name')
    is_expert_db = serializers.SerializerMethodField('is_expert_xref')
    is_active = serializers.SerializerMethodField('is_xref_active')
    first_seen = serializers.CharField(source='created.release_date')
    last_seen = serializers.CharField(source='last.release_date')
    accession = AccessionSerializer()

    def is_expert_xref(self, obj):
        return True if obj.accession.non_coding_id else False

    def is_xref_active(self, obj):
        """
        Return boolean instead of string.
        """
        return True if obj.deleted == 'N' else False

    class Meta:
        model = Xref
        fields = ('database', 'is_expert_db', 'is_active', 'first_seen', 'last_seen', 'taxid', 'accession')


class RnaNestedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for a unique RNAcentral sequence.
    """
    sequence = serializers.Field(source='get_sequence')
    xrefs = serializers.HyperlinkedIdentityField(view_name='rna-xrefs')
    rnacentral_id = serializers.CharField(source='upi')

    class Meta:
        model = Rna
        fields = ('url', 'rnacentral_id', 'md5', 'sequence', 'length', 'xrefs')


class RnaFlatSerializer(RnaNestedSerializer):
    """
    Override the xrefs field in the default nested serializer
    to provide a flat representation.
    """
    xrefs = XrefSerializer()


class RnaFastaSerializer(serializers.ModelSerializer):
    """
    Serializer for presenting RNA sequences in FASTA format
    """
    fasta = serializers.Field(source='get_sequence_fasta')

    class Meta:
        model = Rna
        fields = ('fasta',)


class RnaGffSerializer(serializers.ModelSerializer):
    """
    Serializer for presenting genomic coordinates in GFF format
    """
    gff = serializers.Field(source='get_gff')

    class Meta:
        model = Rna
        fields = ('gff',)


class RnaGff3Serializer(serializers.ModelSerializer):
    """
    Serializer for presenting genomic coordinates in GFF format
    """
    gff3 = serializers.Field(source='get_gff3')

    class Meta:
        model = Rna
        fields = ('gff3',)


class RnaBedSerializer(serializers.ModelSerializer):
    """
    Serializer for presenting genomic coordinates in UCSC BED format
    """
    bed = serializers.Field(source='get_ucsc_bed')

    class Meta:
        model = Rna
        fields = ('bed',)
