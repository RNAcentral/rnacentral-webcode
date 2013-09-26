from portal.models import Rna, Database, Release, Xref
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
    context = dict()
    context['seq_count'] = Rna.objects.count()
    context['db_count']  = Database.objects.count()
    context['last_full_update'] =  Release.objects.filter(release_type='I').order_by('-release_date').all()[0]
    context['last_daily_update'] = Release.objects.filter(release_type='F').order_by('-release_date').all()[0]
    return render(request, 'portal/homepage.html', {'context': context})


def rna_view(request, upi):
    try:
        rna = Rna.objects.get(upi=upi)

        context = dict()
        context['xrefs'] = rna.xrefs.select_related().all()
        context['counts'] = rna.count_symbols()
        context['num_org'] = Xref.objects.filter(upi=upi).values('taxid').distinct().count()
        context['num_db'] = Xref.objects.filter(upi=upi).values('db_id').distinct().count()
        context.update(Xref.objects.filter(upi=upi).\
                                    aggregate(first_seen=Min('created__release_date'),
                                              last_seen=Max('last__release_date')))


    except Rna.DoesNotExist:
        raise Http404
    return render(request, 'portal/rna_view.html', {'rna': rna, 'context': context})
