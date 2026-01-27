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
import os
from datetime import date, timedelta

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Configure sequence search endpoint and proxy settings per environment
if settings.ENVIRONMENT == "DEV":
    SEQUENCE_SEARCH_ENDPOINT = "https://sequence-search-test.rnacentral.org"
    proxies = None
elif settings.ENVIRONMENT == "HX":
    SEQUENCE_SEARCH_ENDPOINT = "https://sequence-search-test.rnacentral.org"
    proxies = {
        "http": "http://hx-wwwcache.ebi.ac.uk:3128",
        "https": "http://hx-wwwcache.ebi.ac.uk:3128",
    }
elif settings.ENVIRONMENT == "HH":
    SEQUENCE_SEARCH_ENDPOINT = "https://sequence-search-test.rnacentral.org"
    proxies = {
        "http": "http://hh-wwwcache.ebi.ac.uk:3128",
        "https": "http://hh-wwwcache.ebi.ac.uk:3128",
    }
else:
    # Fallback for any other environment
    SEQUENCE_SEARCH_ENDPOINT = "https://sequence-search-test.rnacentral.org"
    proxies = None


def proxy_request(request, url, method):
    if method == "POST":
        params = request.POST
        if proxies:
            response = requests.post(
                url, params=params, json=request.data, proxies=proxies
            )
        else:
            response = requests.post(url, params=params, json=request.data)
    elif method == "GET":
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
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_job(request):
    """Submit a job to sequence search service."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/submit-job"
    return proxy_request(request, url, "POST")


@never_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def job_status(request, job_id):
    """Displays status of a job."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/job-status/" + job_id
    return proxy_request(request, url, "GET")


@never_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def job_results(request, job_id):
    """Displays results of a finished job."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/facets-search/" + job_id
    return proxy_request(request, url, "GET")


@never_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def infernal_job_status(request, job_id):
    """Displays status of infernal job."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/infernal-status/" + job_id
    return proxy_request(request, url, "GET")


@never_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def infernal_job_results(request, job_id):
    """Displays results of a finished infernal job."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/infernal-result/" + job_id
    return proxy_request(request, url, "GET")


@never_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def show_searches(request):
    """Displays info about searches."""
    url = SEQUENCE_SEARCH_ENDPOINT + "/api/show-searches"
    return proxy_request(request, url, "GET")


def dashboard(request):
    """Info about searches in rnacentral-sequence-search."""
    all_searches, searches_last_24_hours, searches_last_week = 0, 0, 0
    average_all_searches, average_last_24_hours, average_last_week = 0, 0, 0
    (
        average_high_priority_searches,
        average_last_24_hours_high_priority,
        average_last_week_high_priority,
    ) = (0, 0, 0)
    searches_per_month = None
    expert_db_results = None
    if "test" in request.build_absolute_uri():
        show_searches_url = "https://sequence-search-test.rnacentral.org/api/show-searches"
    else:
        show_searches_url = "https://sequence-search.rnacentral.org/api/show-searches"

    try:
        response_url = requests.get(show_searches_url)
        if response_url.status_code == 200:
            data = response_url.json()
            searches_last_24_hours = data["last_24_hours_result"]["count"]
            average_last_24_hours = data["last_24_hours_result"]["avg_time"]
            average_last_24_hours_high_priority = data["high_priority_24_hours_result"][
                "avg_time"
            ]
            searches_last_week = data["last_week_result"]["count"]
            average_last_week = data["last_week_result"]["avg_time"]
            average_last_week_high_priority = data["high_priority_last_week_result"][
                "avg_time"
            ]
            searches_per_month = data["searches_per_month"]
            expert_db_results = data["expert_db_results"]

    except requests.exceptions.HTTPError as err:
        raise err

    current_date = date.today()
    current_month = current_date.strftime("%Y-%m")
    last_month = (current_date.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    current_month_pie_chart = []
    last_month_pie_chart = []

    for index in range(len(expert_db_results)):
        for key in expert_db_results[index]:
            get_current_month = (
                list(expert_db_results[index][key][-1])
                if list(expert_db_results[index][key])
                else None
            )
            get_current_month = get_current_month.pop() if get_current_month else None

            try:
                get_last_month = (
                    list(expert_db_results[index][key][-2])
                    if list(expert_db_results[index][key])
                    else None
                )
                get_last_month = get_last_month.pop() if get_last_month else None
            except IndexError:
                get_last_month = None

            if get_current_month == current_month:
                current_month_pie_chart.append(
                    {key: expert_db_results[index][key][-1][current_month]}
                )
            if get_current_month == last_month:
                last_month_pie_chart.append(
                    {key: expert_db_results[index][key][-1][last_month]}
                )
            if get_last_month == last_month:
                last_month_pie_chart.append(
                    {key: expert_db_results[index][key][-2][last_month]}
                )

    context = {
        "searches_last_24_hours": searches_last_24_hours,
        "searches_last_week": searches_last_week,
        "average_last_24_hours": average_last_24_hours,
        "average_last_week": average_last_week,
        "average_last_24_hours_high_priority": average_last_24_hours_high_priority,
        "average_last_week_high_priority": average_last_week_high_priority,
        "searches_per_month": searches_per_month,
        "expert_db_results": expert_db_results,
        "current_month_pie_chart": current_month_pie_chart,
        "last_month_pie_chart": last_month_pie_chart,
    }

    return render(request, "dashboard.html", {"context": context})
