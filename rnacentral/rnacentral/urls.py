from django.conf.urls import patterns, url, include
from rest_framework import routers
from portal import views

router = routers.DefaultRouter()
router.register(r'rnas', views.RnaViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)