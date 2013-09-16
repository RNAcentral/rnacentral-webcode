from portal.models import Rna, Xref
from rest_framework import viewsets
from portal.serializers import RnaSerializer, XrefSerializer


class RnaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Rna sequences to be viewed or edited.
    """
    queryset = Rna.objects.defer('seq_long').all()
    serializer_class = RnaSerializer
    paginate_by = 10


class XrefViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Xrefs to be viewed or edited.
    """
    queryset = Xref.objects.prefetch_related().all()
    serializer_class = XrefSerializer
    paginate_by = 10