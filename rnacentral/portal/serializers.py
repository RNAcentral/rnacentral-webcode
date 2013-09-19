from portal.models import Rna, Xref, Ac, Database
from rest_framework import serializers


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
		model = Xref
		fields = ('db', 'accession', 'deleted', 'version', 'taxid', 'created', 'last')
		depth = 1


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    xrefs = XrefSerializer(many=True)
    class Meta:
        model = Rna
        fields = ('upi', 'md5', 'sequence', 'xrefs')
