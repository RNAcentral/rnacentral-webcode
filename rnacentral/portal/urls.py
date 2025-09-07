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

import os

from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import re_path
from django.views.generic import RedirectView, TemplateView
from portal import views
from portal.models import EnsemblAssembly

urlpatterns = [
    # homepage
    re_path(r"^$", views.homepage, name="homepage"),
    # unique RNA sequence
    re_path(
        r"^rna/(?P<upi>URS[0-9A-F]{10})/?$",
        views.generic_rna_view,
        name="generic-rna-sequence",
    ),
    # species specific identifier with forward slash
    re_path(
        r"^rna/(?P<upi>URS[0-9A-F]{10})/(?P<taxid>\d+)/?$",
        views.rna_view,
        name="unique-rna-sequence",
    ),
    # species specific identifier with underscore
    re_path(
        r"^rna/(?P<upi>URS[0-9A-F]{10})_(?P<taxid>\d+)/?$",
        views.rna_view_redirect,
        name="unique-rna-sequence-redirect",
    ),
    # expert database
    re_path(
        r"^expert-database/(?P<expert_db_name>[-\w]+)/?$",
        views.expert_database_view,
        name="expert-database",
    ),
    # expert databases
    re_path(
        r"^expert-databases/?$", views.expert_databases_view, name="expert-databases"
    ),
    # text search can route to any page because it will be taken over by Angular
    re_path(
        r"^search/?$",
        views.TemplateView.as_view(template_name="portal/base.html"),
        name="text-search",
    ),
    # coming soon
    re_path(
        r"^(?P<page>coming-soon)/?$", views.StaticView.as_view(), name="coming-soon"
    ),
    # downloads
    re_path(
        r"^downloads/?$",
        views.StaticView.as_view(),
        {"page": "downloads"},
        name="downloads",
    ),
    # external link
    re_path(
        r"^link/(?P<expert_db>[-\w]+)\:(?P<external_id>.+?)/?$",
        views.external_link,
        name="external-link",
    ),
    # help centre
    re_path(r"^help/?$", views.StaticView.as_view(), {"page": "help/faq"}, name="help"),
    re_path(
        r"^help/browser-compatibility/?$",
        views.StaticView.as_view(),
        {"page": "help/browser-compatibility"},
        name="help-browser-compatibility",
    ),
    re_path(
        r"^help/text-search/?$",
        views.StaticView.as_view(),
        {"page": "help/text-search"},
        name="help-text-search",
    ),
    re_path(
        r"^help/qc/?$", views.StaticView.as_view(), {"page": "help/qc"}, name="help-qc"
    ),
    re_path(
        r"^help/rna-target-interactions/?$",
        views.StaticView.as_view(),
        {"page": "help/rna-target-interactions"},
        name="help-rna-target-interactions",
    ),
    re_path(
        r"^help/gene-ontology-annotations/?$",
        views.StaticView.as_view(),
        {"page": "help/gene-ontology-annotations"},
        name="help-gene-ontology-annotations",
    ),
    re_path(
        r"^help/genomic-mapping/?$",
        views.StaticView.as_view(),
        {
            "page": "help/genomic-mapping",
            "assemblies": EnsemblAssembly.objects.filter(selected_genome=True).order_by(
                "ensembl_url"
            ),
        },
        name="help-genomic-mapping",
    ),
    re_path(
        r"^help/link-to-rnacentral/?$",
        views.StaticView.as_view(),
        {"page": "help/link-to-rnacentral"},
        name="linking-to-rnacentral",
    ),
    re_path(
        r"^help/sequence-features/?$",
        views.StaticView.as_view(),
        {"page": "help/sequence-features"},
        name="help-sequence-features",
    ),
    re_path(
        r"^help/public-database/?$",
        views.StaticView.as_view(),
        {"page": "help/public-database"},
        name="help-public-database",
    ),
    re_path(
        r"^help/ftp/?$",
        views.StaticView.as_view(),
        {"page": "help/ftp"},
        name="help-ftp",
    ),
    re_path(
        r"^help/scientific-advisory-board/?$",
        views.StaticView.as_view(),
        {"page": "help/sab"},
        name="help-scientific-advisory-board",
    ),
    re_path(
        r"^help/secondary-structure/?$",
        views.StaticView.as_view(),
        {"page": "help/secondary-structure"},
        name="help-secondary-structure",
    ),
    re_path(
        r"^help/sequence-search/?$",
        views.StaticView.as_view(),
        {"page": "help/sequence-search-help"},
        name="help-sequence-search",
    ),
    re_path(
        r"^help/galaxy/?$",
        views.StaticView.as_view(),
        {"page": "help/galaxy"},
        name="help-galaxy",
    ),
    re_path(
        r"^help/litscan/?$",
        views.litscan_view,
        name="help-litscan",
    ),
    re_path(
        r"^help/litsumm/?$",
        views.StaticView.as_view(),
        {"page": "help/litsumm"},
        name="help-litsumm",
    ),
    re_path(
        r"^help/litsumm/manuscript?$",
        RedirectView.as_view(url="https://arxiv.org/abs/2311.03056"),
        name="litsumm-manuscript",
    ),
    re_path(
        r"^help/team/?$",
        views.StaticView.as_view(),
        {"page": "help/team"},
        name="help-team",
    ),
    # training
    re_path(
        r"^training/?$",
        views.StaticView.as_view(),
        {"page": "training"},
        name="training",
    ),
    # about us
    re_path(
        r"^about-us/?$",
        views.StaticView.as_view(),
        {"page": "about", "blog_url": settings.RELEASE_ANNOUNCEMENT_URL},
        name="about",
    ),
    # API documentation
    re_path(
        r"^api/?$", views.StaticView.as_view(), {"page": "help/api-v1"}, name="api-docs"
    ),
    # contact us
    re_path(
        r"^contact/?$",
        TemplateView.as_view(template_name="portal/contact.html"),
        name="contact-us",
    ),
    # contact us success
    re_path(
        r"^thanks/?$",
        views.StaticView.as_view(),
        {"page": "thanks"},
        name="contact-us-success",
    ),
    # error
    re_path(r"^error/?$", views.StaticView.as_view(), {"page": "error"}, name="error"),
    # status
    re_path(r"^status/?$", views.website_status_view, name="website-status"),
    # genome browser
    re_path(
        r"^genome-browser/?$",
        TemplateView.as_view(template_name="portal/genome-browser.html"),
        name="genome-browser",
    ),
    # proxy for ebeye search and rfam images
    re_path(r"^api/internal/proxy/?$", views.proxy, name="proxy"),
    # r2dt-web
    re_path(
        r"^r2dt/?$", TemplateView.as_view(template_name="portal/r2dt.html"), name="r2dt"
    ),
    # license
    re_path(
        r"^license/?$", views.StaticView.as_view(), {"page": "license"}, name="license"
    ),
    # gene detail
    re_path(
    r"^genes/(?P<name>[A-Za-z0-9_.-]+)/?$",
    views.gene_detail,
    name="gene-detail"

    )



]

# internal API
urlpatterns += [
    # get species tree
    re_path(
        r"^rna/(?P<upi>\w+)/lineage/?$",
        views.get_sequence_lineage,
        name="sequence-lineage",
    ),
]


# sitemaps
def sitemaps(request, section):
    try:
        # section is either empty string for sitemaps index or
        # string e.g. "-expert-databases", note the dash in the beginning
        path_to_xml_file = os.path.join(
            settings.PROJECT_PATH, "rnacentral", "sitemaps", "sitemap%s.xml" % section
        )
        xml_file = open(path_to_xml_file, "rb")
        return FileResponse(xml_file, content_type="text/xml")
    except IOError as e:
        raise Http404


urlpatterns += [re_path(r"^sitemap(?P<section>.*)\.xml$", sitemaps, name="sitemap")]
