"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

# fabric deployment script

import os.path
from fabric.api import *

env.hosts = ['apetrov@ebi-003.ebi.ac.uk']
git_branch = 'django'

def test(base_url="http://localhost:8000/"):
	"""
	Single entry point for all tests.

	Usage:
	fab test # will test localhost
	fab test:http://test.rnacentral.org
	"""
	local('python apiv1/tests.py --base_url=%s' % base_url)
	local('python portal/tests/selenium_tests.py --base_url %s' % base_url)

def deploy():
	"""
	Run on the test server to deploy the latest changes.

	Usage:
	fab deploy
	"""
	# make sure we are on the right branch
	local('git checkout %s' % git_branch)
	# get latest changes
	local('git pull')
	# update git submodules
	this_dir = os.path.dirname(os.path.realpath(__file__))
	parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
	with lcd(parent_dir):
		local('git submodule update')
	# install all python requirements
	local('pip install -r requirements.txt')
	# move static files to the deployment location
	local('python manage.py collectstatic --noinput')
	# TODO: django-compressor offline compression
	# flush memcached
	with settings(warn_only=True):
		local('echo "stats" | nc -U rnacentral/memcached.sock')
	# restart the django app
	local('touch rnacentral/wsgi.py')
