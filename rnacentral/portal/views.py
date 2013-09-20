from portal.models import Rna
from rest_framework import viewsets
from portal.serializers import RnaSerializer, XrefSerializer

from django.http import HttpResponse, Http404
from django.shortcuts import render

class RnaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Rna sequences to be viewed or edited.
    """
    queryset = Rna.objects.defer('seq_long', 'seq_short').select_related().all()
    serializer_class = RnaSerializer
    paginate_by = 10


def index(request):
    return HttpResponse('Hello')


def rna_view(request, upi):
    try:
        rna = Rna.objects.select_related().get(upi=upi)
    except Rna.DoesNotExist:
        raise Http404
    return render(request, 'portal/rna_view.html', {'rna': rna})
