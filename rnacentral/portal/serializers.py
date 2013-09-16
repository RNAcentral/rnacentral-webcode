from portal.models import Rna, Xref
from rest_framework import serializers


class RnaSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='get_sequence')
    class Meta:
        model = Rna
        fields = ('upi', 'crc64', 'md5', 'len', 'sequence')
        depth = 1


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Xref
        fields = ('upi', 'deleted', 'taxid')
        depth = 1