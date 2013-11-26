from portal.models import Rna, Database, Release, Xref, Accessions
from rest_framework import viewsets
from portal.serializers import RnaSerializer
from portal.forms import ContactForm

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.db.models import Min, Max, Count, Avg
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from django.views.generic.edit import FormView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re


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
    context['db_count'] = Database.objects.count()
    context['last_full_update'] = Release.objects.filter(release_type='F').order_by('-release_date').all()[0]
    try:
        context['last_daily_update'] = Release.objects.filter(release_type='I').order_by('-release_date').all()[0]
    except Exception, e:
        context['last_daily_update'] = context['last_full_update']
    return render(request, 'portal/homepage.html', {'context': context})


def rna_view(request, upi):
    try:
        rna = Rna.objects.get(upi=upi.replace('RNA', 'UPI'))
        context = dict()
        context['xrefs'] = rna.xrefs.prefetch_related().all()
        context['counts'] = rna.count_symbols()
        context['num_org'] = context['xrefs'].values('taxid').distinct().count()
        context['num_db'] = context['xrefs'].values('db_id').distinct().count()
        context.update(context['xrefs'].aggregate(first_seen=Min('created__release_date'),
                                                  last_seen=Max('last__release_date')))
        # xref pagination
        xref_paginator = Paginator(context['xrefs'], 5)
        if request.GET.get('xref-page'):
            request.session['xref_page'] = request.GET.get('xref-page')
            xref_page = int(request.session.get('xref_page'))
        else:
            xref_page = 1
        try:
            context['xref_paginator'] = xref_paginator.page(xref_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['xref_paginator'] = xref_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['xref_paginator'] = xref_paginator.page(xref_paginator.num_pages)

        # ref pagination
        ref_paginator = Paginator(rna.refs.all(), 5)
        if request.GET.get('ref-page'):
            request.session['ref_page'] = request.GET.get('ref-page')
            ref_page = int(request.session.get('ref_page'))
        else:
            ref_page = 1
        try:
            context['ref_paginator'] = ref_paginator.page(ref_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['ref_paginator'] = ref_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['ref_paginator'] = ref_paginator.page(ref_paginator.num_pages)

        rna.upi = rna.upi.replace("UPI", "RNA")  # replace "UPI" with "RNA"
    except Rna.DoesNotExist:
        raise Http404
    return render(request, 'portal/rna_view.html', {'rna': rna, 'context': context})


def search(request):
    if request.REQUEST["rna_type"]:  # todo allowed
        r = Rna.objects.filter(xrefs__accession__feature_name='tRNA').all()
        paginator = Paginator(r, 10)

        page = request.GET.get('page')
        try:
            rnas = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            rnas = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            rnas = paginator.page(paginator.num_pages)

        return render_to_response('portal/search_results.html', {"rnas": rnas})

    else:
        raise Http404()


def expert_database_view(request, expert_db_name):
    context = dict()
    dbs = ('SRPDB', 'MIRBASE', 'VEGA', 'tmRNA_Web')
    if expert_db_name not in dbs:
        expert_db_name = _normalize_expert_db_name(expert_db_name)
    if expert_db_name in dbs:
        data = Rna.objects.filter(xrefs__deleted='N', xrefs__db__descr=expert_db_name)
        context['expert_db'] = Database.objects.get(descr=expert_db_name)
        context['total_sequences'] = data.count()
        context['total_organisms'] = len(data.values('xrefs__taxid').annotate(n=Count("pk")))
        context['examples'] = data.all()[:6]
        for i, example in enumerate(context['examples']):
            context['examples'][i].upi = context['examples'][i].upi.replace("UPI", "RNA")
        context['first_imported'] = data.order_by('xrefs__timestamp')[0].xrefs.all()[0].timestamp
        context['len_counts'] = data.values('len').annotate(counts=Count('len')).order_by('len')
        context.update(data.aggregate(min_length=Min('len'), max_length=Max('len'), avg_length=Avg('len')))
        return render_to_response('portal/expert_database.html', {'context': context})
    elif expert_db_name in ('ENA', 'RFAM'):
        return render_to_response('portal/expert_database_coming_soon.html', {'context': context})
    else:
        raise Http404()


# expert_db_name should match RNACEN.RNC_DATABASE.DESCR
def _normalize_expert_db_name(expert_db_name):
    if re.match('tmrna-website', expert_db_name, flags=re.IGNORECASE):
        return 'tmRNA_Web'
    else:
        return expert_db_name.upper()


class StaticView(TemplateView):
    def get(self, request, page, *args, **kwargs):
        self.template_name = 'portal/flat/' + page + '.html'
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()


class ContactView(FormView):
    template_name = 'portal/contact.html'
    form_class = ContactForm
    success_url = '/thanks/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return HttpResponseRedirect('/thanks/')
