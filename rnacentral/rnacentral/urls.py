from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework import routers
from portal import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'rna', views.RnaViewSet)

urlpatterns = patterns('',
    url(r'^$', 'portal.views.homepage', name='homepage'),
    url(r'^rna/(?P<upi>\w+)$', 'portal.views.rna_view'),
    # admin
    url(r'^admin/', include(admin.site.urls)),
    # flat pages
    url(r'^(?P<page>about|help|thanks|coming-soon)/$', views.StaticView.as_view()),
    url(r'^docs/(?P<page>genome-browsers)/$', views.StaticView.as_view()),
    url(r'^(?P<page>expert-databases)/$', views.StaticView.as_view(), name='expert_databases'),
    # contact us
    url(r'^contact/$', views.ContactView.as_view()),
    # API
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/v1/', include('rest_framework.urls', namespace='rest_framework')),
    # temporary API
    url(r'^xref/(?P<accession>.+)/refs$', 'portal.views.get_literature_references'),
    url(r'^expert-database/(?P<expert_db_name>.+)/lineage$', 'portal.views.get_expert_database_organism_sunburst'),
    # robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # expert databases
    url(r'^expert-database/(?P<expert_db_name>[-\w]+)$', 'portal.views.expert_database_view', name='expert_database'),
    # status page
    url(r'^status/', 'portal.views.website_status_view'),
)
