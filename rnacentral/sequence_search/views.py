"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
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

import requests

from django.conf import settings
from django.views.decorators.cache import never_cache
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .settings import SEQUENCE_SEARCH_ENDPOINT


if settings.ENVIRONMENT == 'DEV':
    proxies = None
elif settings.ENVIRONMENT == 'HX' or settings.ENVIRONMENT == 'OY':
    proxies = {
        'http': 'http://hx-wwwcache.ebi.ac.uk:3128',
        'https': 'http://hx-wwwcache.ebi.ac.uk:3128'
    }
elif settings.ENVIRONMENT == 'PG':
    proxies = {
        'http': 'http://pg-wwwcache.ebi.ac.uk:3128',
        'https': 'http://pg-wwwcache.ebi.ac.uk:3128'
    }


def proxy_request(request, url, method):
    if method == 'POST':
        params = request.POST
        if proxies:
            response = requests.post(url, params=params, json=request.data, proxies=proxies)
        else:
            response = requests.post(url, params=params, json=request.data)
    elif method == 'GET':
        params = request.GET
        if proxies:
            response = requests.get(url, params=params, proxies=proxies)
        else:
            response = requests.get(url, params=params)
    else:
        raise ValueError("Unknown method: %s" % method)

    if response.status_code < 400:
        return Response(response.json(), status=response.status_code)
    else:
        return Response(response.content, status=response.status_code)


@never_cache
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_job(request):
    """Submit a job to sequence search service."""
    url = SEQUENCE_SEARCH_ENDPOINT + '/api/submit-job'
    return proxy_request(request, url, 'POST')


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
def job_status(request, job_id):
    """Displays status of a job."""
    url = SEQUENCE_SEARCH_ENDPOINT + '/api/job-status/' + job_id
    return proxy_request(request, url, 'GET')


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
def job_results(request, job_id):
    """Displays results of a finished job."""
    url = SEQUENCE_SEARCH_ENDPOINT + '/api/facets-search/' + job_id
    return proxy_request(request, url, 'GET')
