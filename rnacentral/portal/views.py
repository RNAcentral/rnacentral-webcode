from portal.models import Rna
from rest_framework import viewsets
from portal.serializers import RnaSerializer, XrefSerializer

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.models import Count, Min, Max

class RnaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Rna sequences to be viewed or edited.
    """
    queryset = Rna.objects.defer('seq_long', 'seq_short').select_related().all()
    serializer_class = RnaSerializer
    paginate_by = 10


def index(request):
    return render(request, 'portal/homepage.html')


def rna_view(request, upi):
    try:
        rna = Rna.objects.filter(upi=upi).order_by('xrefs__accession').annotate(num_org=Count('xrefs__taxid', distinct=True),
                                                   num_db=Count('xrefs__db__id', distinct=True),
                                                   first_seen=Min('xrefs__created__release_date'),
                                                   last_seen=Max('xrefs__last__release_date'))
    except Rna.DoesNotExist:
        raise Http404
    return render(request, 'portal/rna_view.html', {'rna':    rna[0],
                                                    'counts': rna[0].count_symbols()})
