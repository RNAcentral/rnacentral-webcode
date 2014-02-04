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

from portal.models import Rna, Xref, Reference
from rest_framework import serializers


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Xref
        fields = ('db', 'accession', 'deleted', 'version', 'taxid', 'created', 'last', 'refs')
        depth = 1


class RefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = ('authors', 'title', 'location', 'pubmed', 'doi')


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    xrefs = XrefSerializer(many=True)
    refs = RefSerializer(many=True)

    class Meta:
        model = Rna
        fields = ('upi', 'md5', 'sequence', 'xrefs')
