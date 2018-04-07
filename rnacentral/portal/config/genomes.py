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


def url2db(identifier):
    """
    Converts species name from its representation in url to its database representation.
    :param identifier: Species name as in url, e.g. "canis_familiaris"
    :return: Species name as in database "Canis lupus familiaris"
    """
    # special cases
    if identifier in ('canis_familiaris', 'canis_lupus_familiaris'):
        return "Canis lupus familiaris"
    elif identifier in ('gorilla_gorilla', 'gorilla_gorilla_gorilla'):
        return "Gorilla gorilla gorilla"
    elif identifier in ('ceratotherium_simum', 'ceratotherium_simum_simum'):
        return "Ceratotherium simum simum"
    else:
        return identifier.replace('_', ' ').capitalize()


def db2url(identifier):
    """
    Converts species name from its representation in database to url representation.
    :param identifier: Species name as in url, e.g. "Canis lupus familiaris"
    :return: Species name as in database "canis_familiaris"
    """
    # special cases
    if identifier in ("Canis lupus familiaris", "Canis familiaris"):
        return "canis_familiaris"
    elif identifier in ("Gorilla gorilla gorilla", "Gorilla gorilla"):
        return "gorilla_gorilla"
    elif identifier in ("Ceratotherium simum simum", "Ceratotherium simum"):
        return "ceratotherium_simum"
    else:
        return identifier.replace(' ', '_').lower()
