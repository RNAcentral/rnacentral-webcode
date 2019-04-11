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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .settings import SEQUENCE_SEARCH_ENDPOINT


class SubmitJob(APIView):
    """Submit a job to sequence search service."""
    def post(self, request, format=None):
        response = requests.post(SEQUENCE_SEARCH_ENDPOINT + '/submit_job', data=request.data)
        return Response(response.content, status=response.status_code)


class JobStatus(APIView):
    """Displays status of a job."""
    def get(self, request, job_id, format=None):
        response = requests.get(SEQUENCE_SEARCH_ENDPOINT + '/job_status/' + job_id)
        return Response(response.content, status=response.status_code)


class Results(APIView):
    """Displays results of a finished job."""
    def get(self, request, job_id, format=None):
        response = requests.get(SEQUENCE_SEARCH_ENDPOINT + '/results/' + job_id)
        return Response(response.content, status=response.status_code)
