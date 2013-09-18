from portal.models import Rna, Xref
from rest_framework import serializers


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Xref
        fields = ('upi', 'ac', 'taxid')


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    xrefs = XrefSerializer(many=True)
    class Meta:
        model = Rna
        fields = ('upi', 'crc64', 'md5', 'sequence', 'xrefs')
