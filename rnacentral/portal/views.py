from __future__ import print_function

"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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

import json
import os
import random
import re
import requests
import six

if six.PY2:
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render, render_to_response, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic.base import TemplateView

from portal.config.expert_databases import expert_dbs
from portal.models import Rna, Database, Xref, EnsemblAssembly, Publication
from portal.models.rna_precomputed import RnaPrecomputed
from portal.config.svg_images import examples
from portal.rna_summary import RnaSummary

CACHE_TIMEOUT = 60 * 60 * 24 * 1  # per-view cache timeout in seconds
XREF_PAGE_SIZE = 1000

########################
# Function-based views #
########################


@cache_page(CACHE_TIMEOUT)
def get_sequence_lineage(request, upi):
    """
    Internal API.
    Get the lineage for an RNA sequence based on the
    classifications from all database cross-references.
    """
    try:
        queryset = Xref.objects.filter(upi=upi).select_related('accession')
        results = queryset.filter(deleted='N')
        if not results.exists():
            results = queryset
        json_lineage_tree = _get_json_lineage_tree(results.iterator())
    except Rna.DoesNotExist:
        raise Http404
    return HttpResponse(json_lineage_tree, content_type="application/json")


@cache_page(1)
def homepage(request):
    """RNAcentral homepage."""
    random.shuffle(examples)
    context = {
        'databases': list(Database.objects.filter(alive='Y').order_by('?').all()),
        'blog_url': settings.RELEASE_ANNOUNCEMENT_URL,
        'svg_images': examples,
    }

    return render(request, 'portal/homepage.html', {'context': context})


@cache_page(CACHE_TIMEOUT)
def expert_databases_view(request):
    """List of RNAcentral expert databases."""
    expert_dbs.sort(key=lambda x: x['name'].lower())
    expert_dbs.sort(key=lambda x: x['imported'], reverse=True)
    context = {
        'expert_dbs': expert_dbs,
        'num_dbs': len(expert_dbs) - 1,  # Vega is archived
        'num_imported': len([x for x in expert_dbs if x['imported']]) - 1,  # Vega
    }
    return render(request, 'portal/expert-databases.html', {'context': context})


@cache_page(CACHE_TIMEOUT)
def rna_view_redirect(request, upi, taxid):
    """Redirect from urs_taxid to urs/taxid."""
    return redirect('unique-rna-sequence', upi=upi, taxid=taxid, permanent=True)


@cache_page(CACHE_TIMEOUT)
def rna_view(request, upi, taxid=None):
    """
    Unique RNAcentral Sequence view.
    Display all annotations or customize the page using the taxid (optional).
    """
    # get Rna or die
    upi = upi.upper()
    try:
        rna = Rna.objects.get(upi=upi)
    except Rna.DoesNotExist:
        raise Http404

    try:
        precomputed = RnaPrecomputed.objects.filter(upi=upi, taxid=taxid).get()
    except RnaPrecomputed.DoesNotExist:
        precomputed = None

    # if taxid is given, but the RNA does not have annotations for this taxid, redirect to an error page
    if taxid and not precomputed:
        response = redirect('unique-rna-sequence', upi=upi)
        response['Location'] += '?taxid-not-found={taxid}'.format(taxid=taxid)
        return response

    taxid_filtering = True if taxid else False

    symbol_counts = rna.count_symbols()
    non_canonical_base_counts = {key: symbol_counts[key] for key in symbol_counts if key not in ['A', 'U', 'G', 'C']}

    summary = RnaSummary(upi, taxid, settings.EBI_SEARCH_ENDPOINT)
    if taxid_filtering:
        summary_text = render_to_string('portal/summary.html', vars(summary))
        summary_text = re.sub(r'\s+', ' ', summary_text.strip())
        try:
            summary_so_terms = zip(summary.pretty_so_rna_type, summary.so_rna_type)
        except AttributeError:
            summary_so_terms = ''

    # Check if r2dt-web is installed
    path = os.path.join(
        settings.PROJECT_PATH, 'rnacentral', 'portal', 'static', 'r2dt-web', 'dist', 'r2dt-web.js'
    )
    plugin_installed = True if os.path.isfile(path) else False

    # Interactions
    intact = False
    psicquic = False
    interactions = rna.get_intact(taxid)

    for item in interactions:
        if item['intact_id'].startswith('PSICQUIC'):
            split_data = item['intact_id'].split(':')
            item['intact_id'] = split_data[1]
            psicquic = True
        else:
            intact = True

    # Publications
    # get IDs related to the accessed URS
    query_jobs = f'?query=entry_type:metadata%20AND%20primary_id:"{upi}_{taxid}"%20AND%20database:rnacentral&fields=job_id&format=json'
    pub_list = []

    try:
        response = requests.get(settings.EBI_SEARCH_ENDPOINT + query_jobs).json()
        entries = response['entries']
        for entry in entries:
            pub_list.append(entry['fields']['job_id'][0])
    except (IndexError, KeyError):
        pass

    # get number of articles
    if pub_list:
        query_ids = ['job_id:"' + item + '"' for item in pub_list]
        query_ids = '%20OR%20'.join(query_ids)
        query = f'?query=entry_type:Publication%20AND%20({query_ids})&format=json'

        try:
            response = requests.get(settings.EBI_SEARCH_ENDPOINT + query).json()
            pub_count = response['hitCount']
        except KeyError:
            pub_count = None

    else:
        pub_count = None

    # get tab
    tab = request.GET.get('tab', '').lower()
    if tab == '2d':
        active_tab = 2
    elif tab == 'pub':
        active_tab = 3
    else:
        active_tab = 0

    context = {
        'upi': upi,
        'symbol_counts': symbol_counts,
        'non_canonical_base_counts': non_canonical_base_counts,
        'taxid': taxid,
        'taxid_filtering': taxid_filtering,
        'taxid_not_found': request.GET.get('taxid-not-found', ''),
        'active_tab': active_tab,
        'summary_text': summary_text if taxid_filtering else '',
        'summary': summary,
        'summary_so_terms': summary_so_terms if taxid_filtering else '',
        'precomputed': precomputed,
        'mirna_regulators': rna.get_mirna_regulators(taxid=taxid),
        'annotations_from_other_species': rna.get_annotations_from_other_species(taxid=taxid),
        'interactions': interactions,
        'intact': intact,
        'psicquic': psicquic,
        'plugin_installed': plugin_installed,
        'pub_count': pub_count,
    }
    response = render(request, 'portal/sequence.html', {'rna': rna, 'context': context})
    # define canonical URL for Google
    response['Link'] = '<{}>; rel="canonical"'.format(request.build_absolute_uri()).replace('http://', 'https://')
    # ask Google not to index non-species specific pages
    if not taxid:
        response['X-Robots-Tag'] = 'noindex'
    # if the request comes from the API URL, add the header to allow cross domain request
    try:
        response.headers.add('Access-Control-Allow-Origin', '*')
    except AttributeError:
        pass
    return response


@cache_page(CACHE_TIMEOUT)
def expert_database_view(request, expert_db_name):
    """Expert database view."""
    expert_db_name = expert_db_name.upper()
    expert_db = None
    for db in expert_dbs:
        if db['name'].upper() == expert_db_name and db['imported']:
            expert_db = db
        elif db['label'].upper() == expert_db_name.upper() and db['imported']:
            expert_db = db
        elif expert_db_name == 'TMRNA-WEBSITE' and db['label'].upper() == expert_db_name:
            expert_db = db

    if not expert_db:
        raise Http404()

    return render_to_response('portal/expert-database.html', {
        'expert_db': expert_db,
    })


@never_cache
def website_status_view(request):
    """
    This view will be monitored by Nagios for the presence
    of string "All systems operational".
    """
    def _is_database_up():
        try:
            rna = Rna.objects.all()[0]
            return True
        except:
            return False

    def _is_api_up():
        return True

    def _is_search_up():
        return True

    context = dict()
    context['is_database_up'] = _is_database_up()
    context['is_api_up'] = _is_api_up()
    context['is_search_up'] = _is_search_up()
    context['overall_status'] = context['is_database_up'] and context['is_api_up'] and context['is_search_up']
    return render_to_response('portal/website-status.html', {'context': context})


@cache_page(CACHE_TIMEOUT)
def proxy(request):
    """
    Internal API. Used for:
     - EBeye search URL - bypasses EBeye same-origin policy.
     - Rfam and miRBase images - avoids mixed content warnings due to lack of https support in Rfam.
    """
    url = request.GET['url']

    # check domain for security - we don't want someone to abuse this endpoint
    domain = urlparse(url).netloc
    if domain != 'www.ebi.ac.uk' and domain != 'wwwdev.ebi.ac.uk' and domain != 'rfam.org' and domain != 'www.mirbase.org':
        return HttpResponseForbidden("This proxy is for www.ebi.ac.uk, wwwdev.ebi.ac.uk, mirbase.org or rfam.org only.")

    try:
        proxied_response = requests.get(url)
        if proxied_response.status_code == 200:
            if domain == 'rfam.org':  # for rfam images don't forget to set content-type header
                response = HttpResponse(proxied_response.text, content_type="image/svg+xml")
            elif 'mirbase.org' in domain:
                response = HttpResponse(proxied_response.content, content_type="image/png")
            else:
                response = HttpResponse(proxied_response.text)
            return response
        else:
            raise Http404
    except:
        raise Http404


def external_link(request, expert_db, external_id):
    """
    Provide a flexible way to link to RNAcentral by providing a database and external URL.
    """
    search_url = '{base_url}?query=expert_db:"{expert_db}" "{external_id}"&format=json'.format(
        base_url=settings.EBI_SEARCH_ENDPOINT,
        expert_db=expert_db,
        external_id=external_id)
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if data['hitCount'] == 1:
                upi, taxid = data['entries'][0]['id'].split('_')
                return redirect('unique-rna-sequence', upi=upi, taxid=int(taxid))
            else:
                return redirect('/search?q=expert_db:"{}" "{}"'.format(expert_db, external_id))
    except:
        return redirect('/search?q=expert_db:"{}" "{}"'.format(expert_db, external_id))


@cache_page(60 * 10)
def publications_view(request):
    """Dashboard for publications"""
    # get data
    data = Publication.objects.all().order_by('database')

    # count number of ids
    number_of_ids = 0
    for item in data:
        number_of_ids += item.total_ids

    # get number of entries
    query = f'?query=entry_type:Publication&format=json'
    try:
        response = requests.get(settings.EBI_SEARCH_ENDPOINT + query).json()
        hit_count = response['hitCount']
    except KeyError:
        hit_count = None

    context = {
        'data': data,
        'number_of_ids': number_of_ids,
        'hit_count': hit_count
    }

    return render(request, 'portal/litscan-dashboard.html', {'context': context})


#####################
# Class-based views #
#####################

class StaticView(TemplateView):
    """Render flat pages."""
    def get(self, request, page, *args, **kwargs):
        self.template_name = 'portal/' + page + '.html'
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()


class GenomeBrowserView(TemplateView):
    """Render genome-browser, taking into account start/end locations."""
    def get(self, request, *args, **kwargs):
        self.template_name = 'portal/genome-browser.html'

        # if species is not defined - use homo_sapiens as default, if specified and wrong - 404
        if 'species' in request.GET:
            kwargs['genome'] = request.GET['species']
            try:
                ensembl_assembly = EnsemblAssembly.objects.filter(ensembl_url=kwargs['genome']).all()[0]
            except IndexError:
                raise Http404
        else:
            kwargs['genome'] = 'homo_sapiens'
            ensembl_assembly = EnsemblAssembly.objects.get(ensembl_url='homo_sapiens')

        # require chromosome, start and end in kwargs or use default location for this species
        if ('chromosome' in request.GET or 'chr' in request.GET) and 'start' in request.GET and 'end' in request.GET:
            if 'chromosome' in request.GET:
                kwargs['chromosome'] = request.GET['chromosome']
            elif 'chr' in request.GET:
                kwargs['chromosome'] = request.GET['chr']
            kwargs['start'] = request.GET['start']
            kwargs['end'] = request.GET['end']
        else:
            kwargs['chromosome'] = ensembl_assembly.example_chromosome
            kwargs['start'] = ensembl_assembly.example_start
            kwargs['end'] = ensembl_assembly.example_end

        response = super(GenomeBrowserView, self).get(request, *args, **kwargs)
        return response.render()


####################
# Helper functions #
####################


def _get_json_lineage_tree(xrefs):
    """
    Combine lineages from multiple xrefs to produce a single species tree.
    The data are used by the d3 library.
    """

    def get_lineages_and_taxids():
        """Combine the lineages from all accessions in a single list."""
        if isinstance(xrefs, list):
            for xref in xrefs:
                lineages.add(xref[0])
                taxids[xref[0].split('; ')[-1]] = xref[1]
        else:
            for xref in xrefs:
                lineages.add(xref.accession.classification)
                taxids[xref.accession.classification.split('; ')[-1]] = xref.taxid

    def build_nested_dict_helper(path, text, container):
        """Recursive function that builds the nested dictionary."""
        segs = path.split('; ')
        head = segs[0]
        tail = segs[1:]
        if not tail:
            # store how many time the species is seen
            try:
                if head in container:
                    container[head] += 1
                else:
                    container[head] = 1
            except:
                container = {}
                container[head] = 1
        else:
            try:
                if head not in container:
                    container[head] = {}
            except:
                container = {}
                container[head] = 1
            build_nested_dict_helper('; '.join(tail), text, container[head])

    def get_nested_dict(lineages):
        """
        Transform a list like this:
            items = [
                'A; C; X; human',
                'A; C; X; human',
                'B; D; Y; mouse',
                'B; D; Z; rat',
                'B; D; Z; rat',
            ]
        into a nested dictionary like this:
            {'root': {'A': {'C': {'X': {'human': 2}}}, 'B': {'D': {'Y': {'mouse': 1}, 'Z': {'rat': 2}}}}}
        """
        container = {}
        for lineage in lineages:
            build_nested_dict_helper(lineage, lineage, container)
        return container

    def get_nested_tree(data, container):
        """
        Transform a nested dictionary like this:
            {'root': {'A': {'C': {'X': {'human': 2}}}, 'B': {'D': {'Y': {'mouse': 1}, 'Z': {'rat': 2}}}}}
        into a json file like this (fragment shown):
            {"name":"A","children":[{"name":"C","children":[{"name":"X","children":[{"name":"human","size":2}]}]}]}
        """
        if not container:
            container = {
                "name": 'All',
                "children": []
            }
        for name, children in six.iteritems(data):
            if isinstance(children, int):
                container['children'].append({
                    "name": name,
                    "size": children,
                    "taxid": taxids[name],
                })
            else:
                container['children'].append({
                    "name": name,
                    "children": []
                })
                get_nested_tree(children, container['children'][-1])
        return container

    lineages = set()
    taxids = dict()
    get_lineages_and_taxids()
    nodes = get_nested_dict(lineages)
    json_lineage_tree = get_nested_tree(nodes, {})
    return json.dumps(json_lineage_tree)


def handler500(request, *args, **argv):
    """
    Customized version of handler500 with status_code = 200 in order
    to make EBI load balancer to proxy pass to this view, instead of displaying 500.

    https://stackoverflow.com/questions/17662928/django-creating-a-custom-500-404-error-page
    """
    # warning: in django2 signature of this function has changed
    response = render_to_response("500.html", {})
    response.status_code = 200
    return response
