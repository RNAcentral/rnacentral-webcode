"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

from django import template
from django.conf import settings
from portal.config.expert_databases import expert_dbs

register = template.Library()


@register.assignment_tag
def get_expert_databases_columns():
	"""
	Return expert databases grouped and order for the website footer.
	"""
	dbs = sorted(expert_dbs, key=lambda x: x['name'].lower())
	return [
				dbs[:10],
				dbs[10:20],
				dbs[20:30],
				dbs[30:],
			]

@register.assignment_tag
def get_expert_databases_list():
    """
    Get an alphabetically sorted list of imported expert databases.
    """
    imported_dbs = [x for x in expert_dbs if x['imported']]
    return sorted(imported_dbs, key=lambda x: x['name'].lower())

@register.simple_tag
def get_ebi_search_endpoint():
    """
    Get a settings value so that it can be added to the template and
    passed to javascript.
    """
    return settings.EBI_SEARCH_ENDPOINT
