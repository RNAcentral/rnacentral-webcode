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
"""

from portal.models import Rna, Xref, Reference, Database, Accession, Release, Reference, Reference_map
from rest_framework import serializers


class RefSerializer(serializers.HyperlinkedModelSerializer):
    authors = serializers.CharField(source='data.authors')
    publication = serializers.CharField(source='data.location')
    pubmed_id = serializers.CharField(source='data.pubmed')
    doi = serializers.CharField(source='data.doi')
    title = serializers.Field(source='data.get_title')

    class Meta:
        model = Reference_map
        fields = ('title', 'authors', 'publication', 'pubmed_id', 'doi')


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(source='accession')
    is_expert_db = serializers.SerializerMethodField('is_expert_xref')
    citations = serializers.HyperlinkedIdentityField(view_name='accession-citations')
    ena_url = serializers.Field(source='get_ena_url')
    expert_db_url = serializers.Field(source='get_expert_db_external_url')

    def is_expert_xref(self, obj):
        return True if obj.non_coding_id else False

    class Meta:
        model = Accession
        fields = ('url', 'id', 'is_expert_db', 'external_id', 'optional_id', 'feature_name',
                  'division', 'keywords', 'description', 'species', 'organelle',
                  'classification', 'citations', 'ena_url', 'expert_db_url')


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    database = serializers.CharField(source='db.display_name')
    is_active = serializers.SerializerMethodField('is_xref_active')
    first_seen = serializers.CharField(source='created.release_date')
    last_seen = serializers.CharField(source='last.release_date')
    accession = AccessionSerializer()

    def is_xref_active(self, obj):
        return True if obj.deleted == 'N' else False

    class Meta:
        model = Xref
        fields = ('database', 'is_active', 'taxid', 'first_seen', 'last_seen', 'accession')


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    xrefs = serializers.HyperlinkedIdentityField(view_name='rna-xrefs')
    rnacentral_id = serializers.CharField(source='upi')

    class Meta:
        model = Rna
        fields = ('url', 'rnacentral_id', 'md5', 'sequence', 'length', 'xrefs')
