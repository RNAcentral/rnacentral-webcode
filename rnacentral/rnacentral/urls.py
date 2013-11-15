from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework import routers
from portal import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'rna', views.RnaViewSet)

urlpatterns = patterns('',
    url(r'^$', 'portal.views.index'),
    url(r'^rna/(?P<upi>\w+)$', 'portal.views.rna_view'),
    # admin
    url(r'^admin/', include(admin.site.urls)),
    # flat pages
    url(r'^(?P<page>about|help|thanks|coming-soon|genome-browsers)/$', views.StaticView.as_view()),
    # contact us
    url(r'^contact/$', views.ContactView.as_view()),
    # API
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/v1/', include('rest_framework.urls', namespace='rest_framework')),
    # robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # expert databases
    url(r'^expert-database/(?P<expert_db_name>\w+)$', 'portal.views.expert_database_view'),
    # haystack search
    url(r'^search/', include('haystack.urls')),
    # search test
    url(r'^search2/', 'portal.views.search'),
)
