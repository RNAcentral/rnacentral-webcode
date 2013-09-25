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

    # haystack search
    url(r'^search/', include('haystack.urls')),

    url(r'^admin/', include(admin.site.urls)),

	# Wire up our API using automatic URL routing.
	# Additionally, we include login URLs for the browseable API.
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/v1/', include('rest_framework.urls', namespace='rest_framework'))
)