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
from django.db.models import Max, IntegerField, F, Func, CharField
from django.db.models.functions import Cast

if six.PY2:
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control, cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from portal.config.expert_databases import expert_dbs
from portal.config.go_dataset import go_set
from portal.config.summaries import litsumm_examples
from portal.config.svg_images import examples
from portal.models import (
    Database,
    EnsemblAssembly,
    GoAnnotation,
    LitScanStatistics,
    LitSumm,
    Rna,
    Taxonomy,
    Xref,
    Gene,
    GeneMetadata,
    GoflowResults
)
from portal.models.rna_precomputed import RnaPrecomputed
from portal.rna_summary import RnaSummary
from portal.models.gene import GeneMember
from django.db import connection, DatabaseError, connections

CACHE_TIMEOUT = 60 * 60 * 24 * 1  # per-view cache timeout in seconds
XREF_PAGE_SIZE = 1000

########################
# Function-based views #
########################


def get_ensembl_genes(upi, taxid):
        """
        Get Ensembl gene IDs associated with an RNA sequence.
        Returns a list of gene IDs from Ensembl databases.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT xref.upi, xref.taxid, acc.gene 
                FROM rnc_accessions acc 
                JOIN xref ON xref.ac = acc.accession 
                WHERE xref.deleted = 'N' 
                AND xref.upi = %s 
                AND xref.taxid = %s 
                AND acc.database IN ('ENSEMBL', 'ENSEMBL_GENCODE', 'ENSEMBL_FUNGI', 'ENSEMBL_PROTISTS', 'ENSEMBL_METAZOA', 'ENSEMBL_PLANTS')
            """, [upi, taxid])
            
            results = cursor.fetchall()
            return [row[2] for row in results] 


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


@cache_page(CACHE_TIMEOUT)
@cache_control(max_age=0)
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
        summary_text = render_to_string("portal/summary.html", vars(summary))
        summary_text = re.sub(r"\s+", " ", summary_text.strip())
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
        query_jobs = (
            f'?query=entry_type:metadata%20AND%20primary_id:"{upi}_{taxid}"%20AND%20database:rnacentral&'
            f"fields=job_id&format=json"
        )
        pub_list = [upi + "_" + taxid]

        # get IDs related to the URS
        try:
            response = requests.get(
                settings.EBI_SEARCH_ENDPOINT + "-litscan" + query_jobs
            ).json()
            entries = response["entries"]
            for entry in entries:
                pub_list.append(entry["fields"]["job_id"][0])
        except (IndexError, KeyError):
            pass

        # get number of articles
        query_ids = ['job_id:"' + item + '"' for item in pub_list]
        query_ids = "%20OR%20".join(query_ids)
        query = f"?query=entry_type:Publication%20AND%20({query_ids})&format=json"

        try:
            response = requests.get(
                settings.EBI_SEARCH_ENDPOINT + "-litscan" + query
            ).json()
            pub_count = response["hitCount"]
        except KeyError:
            pub_count = None

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
    # Replace the old summary.genes logic with direct database query
    ensembl_genes = get_ensembl_genes(upi, taxid)
    if expression_atlas and ensembl_genes:
        expression_atlas = True
    else:
        expression_atlas = False

    # get tab
    tab = request.GET.get("tab", "").lower()
    if tab == "2d":
        active_tab = 3
    elif tab == "pub":
        active_tab = 6
    else:
        active_tab = 0
    goflow_results = None
    if taxid:
        try:
            urs_taxid = f"{upi}_{taxid}"
            goflow_results = GoflowResults.objects.filter(urs_taxid=urs_taxid).first()

            if goflow_results:
                goflow_data = {
                    'urs_taxid': goflow_results.urs_taxid,
                    'rna_id': goflow_results.rna_id,
                    'pmcid': goflow_results.pmcid,
                    'mirna_binding_filter_result': goflow_results.mirna_binding_filter_result,
                    'mirna_cluster_result': goflow_results.mirna_cluster_result,
                    'binding_type_filter_result': goflow_results.binding_type_filter_result,
                    'experimental_evidence_result': goflow_results.experimental_evidence_result,
                    'functional_interaction_result': goflow_results.functional_interaction_result,
                    'mirna_mrna_binding_result': goflow_results.mirna_mrna_binding_result,
                    'effect_endogenous_2_result': goflow_results.effect_endogenous_2_result,
                    'computational_prediction_result': goflow_results.computational_prediction_result,
                    'validated_binding_only_result': goflow_results.validated_binding_only_result,
                    'mrna_expression_assay_result': goflow_results.mrna_expression_assay_result,
                    
                    # Reasoning
                    'mirna_binding_filter_reasoning': goflow_results.mirna_binding_filter_reasoning,
                    'mirna_cluster_reasoning': goflow_results.mirna_cluster_reasoning,
                    'binding_type_filter_reasoning': goflow_results.binding_type_filter_reasoning,
                    'experimental_evidence_reasoning': goflow_results.experimental_evidence_reasoning,
                    'functional_interaction_reasoning': goflow_results.functional_interaction_reasoning,
                    'mirna_mrna_binding_reasoning': goflow_results.mirna_mrna_binding_reasoning,
                    'effect_endogenous_2_reasoning': goflow_results.effect_endogenous_2_reasoning,
                    'computational_prediction_reasoning': goflow_results.computational_prediction_reasoning,
                    'validated_binding_only_reasoning': goflow_results.validated_binding_only_reasoning,
                    'mrna_expression_assay_reasoning': goflow_results.mrna_expression_assay_reasoning,
                    
                    # Evidence
                    'mirna_binding_filter_evidence': goflow_results.mirna_binding_filter_evidence,
                    'mirna_cluster_evidence': goflow_results.mirna_cluster_evidence,
                    'binding_type_filter_evidence': goflow_results.binding_type_filter_evidence,
                    'experimental_evidence_evidence': goflow_results.experimental_evidence_evidence,
                    'functional_interaction_evidence': goflow_results.functional_interaction_evidence,
                    'mirna_mrna_binding_evidence': goflow_results.mirna_mrna_binding_evidence,
                    'effect_endogenous_2_evidence': goflow_results.effect_endogenous_2_evidence,
                    'computational_prediction_evidence': goflow_results.computational_prediction_evidence,
                    'validated_binding_only_evidence': goflow_results.validated_binding_only_evidence,
                    'mrna_expression_assay_evidence': goflow_results.mrna_expression_assay_evidence,
                    
                    # Targets and annotation
                    'targets': goflow_results.targets,
                    'target': goflow_results.target,
                    'target_list': goflow_results.get_target_list(),
                    'annotation': goflow_results.annotation
                }

                # Clean up None values for JSON serialization
                goflow_data = {
                    k: v for k, v in goflow_data.items() 
                    if v is not None and v != ''
                }
            else:
                goflow_data = None
        except GoflowResults.DoesNotExist:
            goflow_data = None
        except Exception as e:
            print(f"Error fetching GoFlow data: {e}")
            goflow_data = None
    else:
        goflow_data = None




    context = {
        "upi": upi,
        "symbol_counts": symbol_counts,
        "non_canonical_base_counts": non_canonical_base_counts,
        "taxid": taxid,
        "taxid_filtering": taxid_filtering,
        "taxid_not_found": request.GET.get("taxid-not-found", ""),
        "active_tab": active_tab,
        "summary_text": summary_text if taxid_filtering else "",
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
        "goflow_results": goflow_results,  # Keep for backward compatibility
        "goflow_data": goflow_data,        # Enhanced data for component
        "goflow_data_json": json.dumps(goflow_data) if goflow_data else None,
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
def gene_detail(request, name):
    """
    Gene detail view for genes with format public_name.version
    - If name contains version (e.g., "RNACG12082614835.5"): fetch exact gene
    - If no version (e.g., "RNACG12082614835"): fetch latest version for that public name
    """
    
    gene = None
    version = None
    base_name = name
    
    # Parse version from name if it exists
    if '.' in name and name.split('.')[-1].isdigit():
        parts = name.rsplit('.', 1)
        base_name = parts[0]
        version = int(parts[1])
        
        # Look for exact match
        gene = Gene.objects.filter(name=name).first()

    else:
        # No version in name, find latest version
        # Look for all genes starting with "base_name." and get the one with highest version
        versioned_genes = Gene.objects.filter(name__startswith=f"{base_name}.")
        
        if versioned_genes.exists():
            # Extract version numbers and find the highest
            latest_gene = None
            highest_version = -1
            
            for g in versioned_genes:
                try:
                    # Extract version from gene name (e.g., "RNACG12082614835.5" -> 5)
                    gene_version = int(g.name.split('.')[-1])
                    if gene_version > highest_version:
                        highest_version = gene_version
                        latest_gene = g
                        version = gene_version 
                except (ValueError, IndexError):
                    continue
            
            gene = latest_gene
        else:
            # Try exact match without version (fallback)
            gene = Gene.objects.filter(name=base_name).first()
    
    if not gene:
        return render(request, "portal/gene_detail.html", {
            "geneFound": False,
            "geneName": base_name,
            "geneVersion": version,
            "geneData": {},
            "transcriptsData": [],
            "externalLinksData": [],
            "transcriptsPagination": {},
            "litsummSummaries": [],
        })
    
    metadata = getattr(gene, "metadata", None)
    species_name = gene.taxonomy.name if gene.taxonomy else None

    gene_data = {
        "name": gene.name,
        "chromosome": gene.chromosome,
        "startPosition": gene.start,
        "endPosition": gene.stop,
        "strand": gene.strand,
        "strandDirection": "Reverse" if gene.strand == "-" else "Forward",
        "geneType": metadata.ontology_term.name if metadata and metadata.ontology_term else "Unknown",
        "summary": metadata.description if metadata else "No summary available",
        "shortDescription": metadata.short_description if metadata else "",
        "length": abs(gene.stop - gene.start) + 1 if gene.start and gene.stop else 0,
        "version": version,
        "species": species_name.lower().replace(" ", "_")
    }

    # Get pagination params
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))  # Default 10 transcripts per page
  
    # Total count
    with connection.cursor() as cursor:
        cursor.execute("""
         SELECT COUNT(DISTINCT locus.urs_taxid)
            FROM rnc_gene_members gm
            JOIN rnc_genes g ON(gm.rnc_gene_id=g.id)
            JOIN rnc_sequence_regions locus ON locus.id = gm.locus_id
            JOIN rnc_rna_precomputed pre ON pre.id = locus.urs_taxid
            WHERE g.public_name = %s
        """, [gene.name])
        total_count = cursor.fetchone()[0]

    # Calculate pagination
    total_pages = (total_count + page_size - 1) // page_size 
    offset = (page - 1) * page_size

    
    # Get current page transcript data
    transcripts_data = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ON (locus.urs_taxid)
                locus.urs_taxid,
                pre.description
            FROM rnc_gene_members gm
            JOIN rnc_genes g ON(gm.rnc_gene_id=g.id)
            JOIN rnc_sequence_regions locus ON locus.id = gm.locus_id
            JOIN rnc_rna_precomputed pre ON pre.id = locus.urs_taxid
            WHERE g.public_name = %s
            ORDER BY locus.urs_taxid
            LIMIT %s OFFSET %s
        """, [gene.name, page_size, offset])
        
        rows = cursor.fetchall()
        
        for row in rows:
            urs_taxid, description = row
            transcript_info = {
                "id": urs_taxid,
                "description": description or "No description available"
            }
            transcripts_data.append(transcript_info)

    # Pagination metadata - convert Python booleans to strings for JavaScript
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "page_size": page_size,
        "has_previous": "true" if page > 1 else "false",
        "has_next": "true" if page < total_pages else "false",
        "previous_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
        "start_index": offset + 1 if total_count > 0 else 0,
        "end_index": min(offset + page_size, total_count),
    }


    # External links data
    external_links_data = []

    # Fetch litsumm summaries for all transcripts of this gene
    litsumm_summaries_data = []

    # Get all litsumm summaries for transcripts of this gene with their descriptions
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ls.primary_id, ls.display_id, ls.summary, pre.description
            FROM rnc_gene_members gm
            JOIN rnc_genes g ON gm.rnc_gene_id = g.id
            JOIN rnc_sequence_regions locus ON locus.id = gm.locus_id
            JOIN litsumm_summaries ls ON ls.primary_id = locus.urs_taxid
            JOIN rnc_rna_precomputed pre ON pre.id = locus.urs_taxid
            WHERE g.public_name = %s
        """, [gene.name])
        rows = cursor.fetchall()

        pmc_regex = re.compile(r"PMC[0-9]+")
        seen_ids = set()
        for row in rows:
            primary_id, display_id, summary, description = row
            # Skip duplicates
            if primary_id in seen_ids:
                continue
            seen_ids.add(primary_id)
            # Convert PMC IDs to links
            summary_with_links = pmc_regex.sub(
                r'<a href="https://europepmc.org/article/PMC/\g<0>" target="_blank">\g<0></a>',
                summary,
            )
            litsumm_summaries_data.append({
                "id": display_id,
                "urs": primary_id,
                "summary": summary_with_links,
                "description": description or "",
            })

    return render(request, "portal/gene_detail.html", {
        "geneName": base_name,
        "geneVersion": version,
        "geneFound": True,
        'geneData': json.dumps(gene_data),
        'transcriptsData': json.dumps(transcripts_data),
        'externalLinksData': json.dumps(external_links_data),
        'transcriptsPagination': json.dumps(pagination),
        'litsummSummaries': json.dumps(litsumm_summaries_data),
    })


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
    This view will be used by Traffic Manager to check for the presence of the
    text "All systems operational". Traffic will be redirected to the HX
    cluster if this function returns a problem.
    """

    def _is_database_up():
        try:
            Database.objects.get(id=1)
            return True
        except (Database.DoesNotExist, DatabaseError, Exception):
            # Catch all database-related exceptions
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
    
    # Return 503 if any system is down
    if not context["overall_status"]:
        response = render(request, "portal/website-status.html", {"context": context})
        response.status_code = 503
        return response
    
    return render(request, "portal/website-status.html", {"context": context})

@never_cache
def health_check(request):
    """
    This will be used by the Traffic Manager to redirect traffic. If it returns a 200x response code everything is fine.
    If 500x is returned, traffic will be redirected to the fallback cluster.
    """

    def check_database_status():
        response = HttpResponse()
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    response.status_code = 200
                    response.content = "OK"
                    return response
                else:
                    response.status_code = 503
                    response.content = "Database is down"
                    return response
        except DatabaseError:
            response.status_code = 503
            response.content = "Database is down"
            return response

        
    def check_api():
        test_endpoint = 'https://rnacentral.org/api/v1/rna/'
        test_id = 'URS0000000001'
        try:
            api_response = requests.get(f"{test_endpoint}{test_id}", timeout=(10, 20))
            if api_response.status_code == 200:
                return HttpResponse("OK", status=200)
            return HttpResponse("API is down", status=503)
        except requests.exceptions.ConnectTimeout:
            return HttpResponse("API is too slow", status=503)
        except requests.RequestException:
            return HttpResponse("API is down", status=503)

    def check_search():
        search_endpoint = 'https://rnacentral.org/search'
        test_query = 'RNA'
        try:
            search_response = requests.get(f"{search_endpoint}?q={test_query}", timeout=(10, 20))
            if search_response.status_code == 200:
                return HttpResponse("OK", status=200)
            return HttpResponse("Search is down", status=503)
        except requests.exceptions.ConnectTimeout:
            return HttpResponse("Search is too slow", status=503)
        except requests.RequestException:
            return HttpResponse("Search is down", status=503)

    context = {}

    # Run checks
    checks = {
        "database": check_database_status(),
        "api": check_api(),
        "search": check_search(),
    }

    # Build structured context for template
    context = {
        name: {
            "status_code": resp.status_code,
            "message": resp.content.decode("utf-8"),
        }
        for name, resp in checks.items()
    }

    # Overall status
    context["overall_status"] = all(
        service["status_code"] == 200 for service in context.values()
        if isinstance(service, dict)
    )

    # Set HTTP status for response
    status_code = 200 if context["overall_status"] else 503
    return render(request, "portal/health-check.html", {"context": context}, status=status_code)


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

@csrf_exempt
def docbot_feedback(request):
    """
    Post DocBot feedback to Doorbell.io.
    Only allow POST requests from whitelisted hosts, then forward to Doorbell.io.
    """
    if request.method != "POST":
        return HttpResponseForbidden("Only POST requests are allowed.")

    # Whitelist of allowed hosts
    allowed_hosts = ["wwwint.ebi.ac.uk"]
    if settings.DEBUG:
        allowed_hosts.extend(["localhost", "127.0.0.1"])

    referer = request.META.get("HTTP_REFERER", "")
    if not any(host in referer for host in allowed_hosts):
        return HttpResponseForbidden("Invalid referer.")

    # Parse JSON body from request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON in request body."}, status=400
        )

    doorbell_api_key = settings.DOORBELL_API_KEY
    doorbell_api_id = settings.DOORBELL_API_ID
    doorbell_url = f"https://doorbell.io/api/applications/{doorbell_api_id}/submit?key={doorbell_api_key}"

    feedback_data = {
        "message": data.get("message", ""),
        "email": data.get("email", ""),
        "name": data.get("name", ""),
        "url": data.get("url", referer),
        "properties": {
            "source": "DocBot",
        },
    }

    try:
        response = requests.post(doorbell_url, json=feedback_data)
        if response.status_code == 201:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to submit feedback."}, status=500
            )
    except requests.RequestException:
        return JsonResponse(
            {"status": "error", "message": "An error occurred while submitting feedback."},
            status=500,
        )


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