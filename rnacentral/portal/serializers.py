from portal.models import Rna, Xref, Ac, Database, Reference
from rest_framework import serializers


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
		model = Xref
		fields = ('db', 'accession', 'deleted', 'version', 'taxid', 'created', 'last')
		depth = 1


class RefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
		model = Reference
		fields = ('authors', 'title', 'location', 'pubmed', 'doi', 'publisher', 'editors')


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    xrefs = XrefSerializer(many=True)
    refs = RefSerializer(many=True)
    class Meta:
        model = Rna
        fields = ('upi', 'md5', 'sequence', 'xrefs', 'refs')
