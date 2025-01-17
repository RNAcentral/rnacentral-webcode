from __future__ import print_function

"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
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

from django.conf import settings
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic.base import TemplateView
from portal.config.expert_databases import expert_dbs
from portal.config.go_dataset import go_set
from portal.config.summaries import litsumm_examples
from portal.config.svg_images import examples
from portal.models import (
    Database,
    EnsemblAssembly,
    GoAnnotation,
    LitScanJob,
    LitScanMetadata,
    LitScanStatistics,
    LitSumm,
    Rna,
    Taxonomy,
    Xref,
)
from portal.models.rna_precomputed import RnaPrecomputed
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
    Get the lineage for an RNA sequence from all database cross-references.
    """
    try:
        xref = Xref.objects.filter(upi=upi).distinct("taxid")
        results = xref.filter(deleted="N")
        if not results.exists():
            results = xref
        queryset = Taxonomy.objects.none()
        for item in results:
            queryset |= Taxonomy.objects.filter(id=item.taxid)
        json_lineage_tree = _get_json_lineage_tree(queryset.iterator())
    except Rna.DoesNotExist:
        raise Http404
    return HttpResponse(json_lineage_tree, content_type="application/json")


@cache_page(1)
def homepage(request):
    """RNAcentral homepage."""
    random.shuffle(examples)
    random.shuffle(litsumm_examples)
    summaries = []

    for item in litsumm_examples:
        regex = re.compile("PMC[0-9]+")
        get_summary = LitSumm.objects.filter(primary_id=item["urs"]).first()
        summary = regex.sub(
            r'<a href="https://europepmc.org/article/PMC/\g<0>" target="blank">\g<0></a>',
            get_summary.summary,
        )
        summaries.append(
            {
                "id": item["id"],
                "title": item["description"],
                "urs": item["urs"],
                "summary": summary,
            }
        )

    context = {
        "databases": list(Database.objects.filter(alive="Y").order_by("?").all()),
        "blog_url": settings.RELEASE_ANNOUNCEMENT_URL,
        "svg_images": examples,
        "summaries": summaries,
    }

    return render(request, "portal/homepage.html", {"context": context})


@cache_page(CACHE_TIMEOUT)
def expert_databases_view(request):
    """List of RNAcentral expert databases."""
    expert_dbs.sort(key=lambda x: x["name"].lower())
    expert_dbs.sort(key=lambda x: x["imported"], reverse=True)
    context = {
        "expert_dbs": expert_dbs,
        "num_dbs": len(expert_dbs) - 1,  # Vega is archived
        "num_imported": len([x for x in expert_dbs if x["imported"]]) - 1,  # Vega
    }
    return render(request, "portal/expert-databases.html", {"context": context})


@cache_page(CACHE_TIMEOUT)
def rna_view_redirect(request, upi, taxid):
    """Redirect from urs_taxid to urs/taxid."""
    return redirect("unique-rna-sequence", upi=upi, taxid=taxid, permanent=True)


@cache_page(CACHE_TIMEOUT)
def generic_rna_view(request, upi):
    """Generic sequence page."""

    # get RNA or die
    upi = upi.upper()
    try:
        rna = Rna.objects.get(upi=upi)
    except Rna.DoesNotExist:
        raise Http404

    # get precomputed for this UPI
    try:
        precomputed = RnaPrecomputed.objects.filter(upi=upi)
    except RnaPrecomputed.DoesNotExist:
        precomputed = None

    # get unique dbs
    dbs = []
    for urs in precomputed:
        get_dbs = urs.get_databases()

        if get_dbs:
            for db in get_dbs:
                dbs.append(db) if db not in dbs else None

    context = {
        "db_length": len(dbs),
        "dbs": ", ".join(dbs) if dbs else None,
        "precomputed": precomputed,
        "rna_length": rna.length,
        "upi": upi,
    }

    return render(request, "portal/generic-sequence.html", context)


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
        response = redirect("unique-rna-sequence", upi=upi)
        response["Location"] += "?taxid-not-found={taxid}".format(taxid=taxid)
        return response

    taxid_filtering = True if taxid else False

    symbol_counts = rna.count_symbols()
    non_canonical_base_counts = {
        key: symbol_counts[key]
        for key in symbol_counts
        if key not in ["A", "U", "G", "C"]
    }

    summary = RnaSummary(upi, taxid, settings.EBI_SEARCH_ENDPOINT)
    if taxid_filtering:
        try:
            summary_so_terms = zip(summary.pretty_so_rna_type, summary.so_rna_type)
        except AttributeError:
            summary_so_terms = ""

    # get litsumm summary
    if taxid:
        litsumm_summary = LitSumm.objects.filter(primary_id=upi + "_" + taxid)
        regex = re.compile("PMC[0-9]+")

        for item in litsumm_summary:
            item.summary = regex.sub(
                r'<a href="https://europepmc.org/article/PMC/\g<0>" target="blank">\g<0></a>',
                item.summary,
            )
    else:
        litsumm_summary = None

    # Check if r2dt-web is installed
    path = os.path.join(
        settings.PROJECT_PATH,
        "rnacentral",
        "portal",
        "static",
        "r2dt-web",
        "dist",
        "r2dt-web.js",
    )
    plugin_installed = True if os.path.isfile(path) else False

    # Publications
    if taxid:
        # get IDs related to the URS
        related_ids = (
            LitScanMetadata.objects.filter(primary_id__iexact=upi + "_" + taxid)
            .values_list("job_id", flat=True)
            .distinct()
        )

        # get number of articles
        pub_count = LitScanJob.objects.filter(job_id__in=related_ids).aggregate(
            Sum("hit_count")
        )["hit_count__sum"]
    else:
        pub_count = None

    # get go_term_id for swissbiopics library
    if taxid:
        go_term_id = []
        go_annotation = GoAnnotation.objects.filter(
            rna_id=upi + "_" + taxid, qualifier="part_of"
        ).select_related("ontology_term", "evidence_code")
        for item in go_annotation:
            if item.ontology_term.ontology_term_id in go_set:
                go_term_id.append(item.ontology_term.ontology_term_id)
        go_term_id = ",".join(go_term_id)
    else:
        go_term_id = None

    # check if we have an xref to Expression Atlas
    expression_atlas = False
    try:
        expression_atlas = Xref.objects.filter(
            upi=upi, taxid=taxid, db__display_name="Expression Atlas"
        ).exists()
    except Xref.DoesNotExist:
        pass

    # we also need gene and species to use the Expression Atlas widget
    if (
        expression_atlas
        and summary.species
        and [item for item in summary.genes if item.startswith("ENS")]
    ):
        expression_atlas = True
    else:
        expression_atlas = False

    # get tab
    tab = request.GET.get("tab", "").lower()
    if tab == "2d":
        active_tab = 2
    elif tab == "pub":
        active_tab = 4
    else:
        active_tab = 0

    context = {
        "upi": upi,
        "symbol_counts": symbol_counts,
        "non_canonical_base_counts": non_canonical_base_counts,
        "taxid": taxid,
        "taxid_filtering": taxid_filtering,
        "taxid_not_found": request.GET.get("taxid-not-found", ""),
        "active_tab": active_tab,
        "summary": summary,
        "summary_so_terms": summary_so_terms if taxid_filtering else "",
        "precomputed": precomputed,
        "mirna_regulators": rna.get_mirna_regulators(taxid=taxid),
        "annotations_from_other_species": rna.get_annotations_from_other_species(
            taxid=taxid
        ),
        "plugin_installed": plugin_installed,
        "pub_count": pub_count,
        "go_term_id": go_term_id,
        "description_as_json_str": json.dumps(precomputed.description),
        "expression_atlas": expression_atlas,
        "interactions": rna.get_intact(taxid),
        "litsumm_summary": litsumm_summary,
    }
    response = render(request, "portal/sequence.html", {"rna": rna, "context": context})
    # define canonical URL for Google
    response["Link"] = '<{}>; rel="canonical"'.format(
        request.build_absolute_uri()
    ).replace("http://", "https://")
    # ask Google not to index non-species specific pages
    if not taxid:
        response["X-Robots-Tag"] = "noindex"
    # if the request comes from the API URL, add the header to allow cross domain request
    try:
        response.headers.add("Access-Control-Allow-Origin", "*")
    except AttributeError:
        pass
    return response


@cache_page(CACHE_TIMEOUT)
def expert_database_view(request, expert_db_name):
    """Expert database view."""
    expert_db_name = expert_db_name.upper()
    expert_db = None
    for db in expert_dbs:
        if db["name"].upper() == expert_db_name and db["imported"]:
            expert_db = db
        elif db["label"].upper() == expert_db_name.upper() and db["imported"]:
            expert_db = db
        elif (
            expert_db_name == "TMRNA-WEBSITE" and db["label"].upper() == expert_db_name
        ):
            expert_db = db

    if not expert_db:
        raise Http404()

    return render(
        request,
        "portal/expert-database.html",
        {
            "expert_db": expert_db,
        },
    )


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
    context["is_database_up"] = _is_database_up()
    context["is_api_up"] = _is_api_up()
    context["is_search_up"] = _is_search_up()
    context["overall_status"] = (
        context["is_database_up"] and context["is_api_up"] and context["is_search_up"]
    )
    return render(request, "portal/website-status.html", {"context": context})


@cache_page(CACHE_TIMEOUT)
def proxy(request):
    """
    Internal API. Used for:
     - EBeye search URL - bypasses EBeye same-origin policy.
     - Rfam and miRBase images - avoids mixed content warnings due to lack of https support in Rfam.
    """
    url = request.GET["url"]

    # check domain for security - we don't want someone to abuse this endpoint
    domain = urlparse(url).netloc
    domain_list = [
        "www.ebi.ac.uk",
        "wwwdev.ebi.ac.uk",
        "rfam.org",
        "www.mirbase.org",
        "rna.bgsu.edu",
    ]
    if domain not in domain_list:
        return HttpResponseForbidden(
            "This proxy is for www.ebi.ac.uk, wwwdev.ebi.ac.uk, mirbase.org, rfam.org or rna.bgsu.edu only."
        )

    if domain == "rna.bgsu.edu":
        # make sure to use the full url
        try:
            query_string = request.META["QUERY_STRING"]
            url = query_string.split("url=")[1]
        except IndexError:
            pass

    try:
        proxied_response = requests.get(url)
        if proxied_response.status_code == 200:
            if (
                domain == "rfam.org"
            ):  # for rfam images don't forget to set content-type header
                response = HttpResponse(
                    proxied_response.text, content_type="image/svg+xml"
                )
            elif "mirbase.org" in domain:
                response = HttpResponse(
                    proxied_response.content, content_type="image/png"
                )
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
    search_url = (
        '{base_url}?query=expert_db:"{expert_db}" "{external_id}"&format=json'.format(
            base_url=settings.EBI_SEARCH_ENDPOINT,
            expert_db=expert_db,
            external_id=external_id,
        )
    )
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if data["hitCount"] == 1:
                upi, taxid = data["entries"][0]["id"].split("_")
                return redirect("unique-rna-sequence", upi=upi, taxid=int(taxid))
            else:
                return redirect(
                    '/search?q=expert_db:"{}" "{}"'.format(expert_db, external_id)
                )
    except:
        return redirect('/search?q=expert_db:"{}" "{}"'.format(expert_db, external_id))


@cache_page(60 * 10)
def litscan_view(request):
    """Get LitScan data"""
    data = LitScanStatistics.objects.first()
    context = {"data": data}
    return render(request, "portal/help/litscan.html", context)


#####################
# Class-based views #
#####################


class StaticView(TemplateView):
    """Render flat pages."""

    def get(self, request, page, *args, **kwargs):
        self.template_name = "portal/" + page + ".html"
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()


class GenomeBrowserView(TemplateView):
    """Render genome-browser, taking into account start/end locations."""

    def get(self, request, *args, **kwargs):
        self.template_name = "portal/genome-browser.html"

        # if species is not defined - use homo_sapiens as default, if specified and wrong - 404
        if "species" in request.GET:
            kwargs["genome"] = request.GET["species"]
            try:
                ensembl_assembly = EnsemblAssembly.objects.filter(
                    ensembl_url=kwargs["genome"]
                ).all()[0]
            except IndexError:
                raise Http404
        else:
            kwargs["genome"] = "homo_sapiens"
            ensembl_assembly = EnsemblAssembly.objects.get(ensembl_url="homo_sapiens")

        # require chromosome, start and end in kwargs or use default location for this species
        if (
            ("chromosome" in request.GET or "chr" in request.GET)
            and "start" in request.GET
            and "end" in request.GET
        ):
            if "chromosome" in request.GET:
                kwargs["chromosome"] = request.GET["chromosome"]
            elif "chr" in request.GET:
                kwargs["chromosome"] = request.GET["chr"]
            kwargs["start"] = request.GET["start"]
            kwargs["end"] = request.GET["end"]
        else:
            kwargs["chromosome"] = ensembl_assembly.example_chromosome
            kwargs["start"] = ensembl_assembly.example_start
            kwargs["end"] = ensembl_assembly.example_end

        response = super(GenomeBrowserView, self).get(request, *args, **kwargs)
        return response.render()


####################
# Helper functions #
####################


def _get_json_lineage_tree(taxonomies):
    """
    Combine lineages from multiple taxonomies to produce a single species tree.
    The data are used by the d3 library.
    """

    def get_lineages_and_taxids():
        """Combine the lineages from all taxonomies in a single list."""
        if isinstance(taxonomies, list):
            # used by portal -> management -> commands -> database_stats.py
            # but not sure if this is still useful
            xrefs = taxonomies  # using xref and rnc_accessions here, not taxonomies
            for xref in xrefs:
                lineages.add(xref[0])
                taxids[xref[0].split("; ")[-1]] = xref[1]
        else:
            for taxonomy in taxonomies:
                lineages.add(taxonomy.lineage)
                taxids[taxonomy.lineage.split("; ")[-1]] = taxonomy.id

    def build_nested_dict_helper(path, text, container):
        """Recursive function that builds the nested dictionary."""
        segs = path.split("; ")
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
            build_nested_dict_helper("; ".join(tail), text, container[head])

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
            container = {"name": "All", "children": []}
        for name, children in six.iteritems(data):
            if isinstance(children, int):
                container["children"].append(
                    {
                        "name": name,
                        "size": children,
                        "taxid": taxids[name],
                    }
                )
            else:
                container["children"].append({"name": name, "children": []})
                get_nested_tree(children, container["children"][-1])
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
    response = render(request, "500.html", {})
    response.status_code = 200
    return response
