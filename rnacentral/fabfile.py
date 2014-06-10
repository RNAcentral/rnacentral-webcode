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
import requests
from fabric.api import *


def test(base_url="http://localhost:8000/"):
	"""
	Single entry point for all tests.

	Usage:
	fab test # will test localhost
	fab test:http://test.rnacentral.org
	"""
	local('python apiv1/tests.py --base_url=%s' % base_url)
	local('python portal/tests/selenium_tests.py --base_url %s --driver=phantomjs' % base_url)
	local('python apiv1/search/sequence/tests.py --base_url %s' % base_url)

def deploy(restart_url="http://rnacentral.org"):
	"""
	Deploy to a server.

	fab.cfg template:
	rnacentral_site=/path/to/manage.py
	activate=source /path/to/virtualenvs/RNAcentral/bin/activate
	ld_library_path=export LD_LIBRARY_PATH=/path/to/oracle/libraries/:$LD_LIBRARY_PATH
	oracle_home=export ORACLE_HOME=/path/to/oracle/libraries/

	Usage:
	fab -H user@server1,user@server2 -c /path/to/fab.cfg deploy:website_url
	"""

	def git_updates():
		"""
		"""
		git_branch = 'django'
		# make sure we are on the right branch
		run('git checkout %s' % git_branch)
		# get latest changes
		run('git pull')
		# update git submodules
		this_dir = os.path.dirname(os.path.realpath(__file__))
		parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
		with cd(parent_dir):
			run('git submodule update')

	def django_updates():
		"""
		* activate virtual environment
		* set Oracle variables
		* install all python requirements
		* move static files to the deployment location
		"""
		with prefix(env['activate']), prefix(env['ld_library_path']), prefix(env['oracle_home']):
			run('pip install -r requirements.txt')
			run('python manage.py collectstatic --noinput')
			# TODO: django-compressor offline compression

	def	flush_memcached():
		"""
		Delete all cached data.
		"""
		with settings(warn_only=True):
			run('echo "flush_all" | nc -U rnacentral/memcached.sock')

	def restart_django():
		"""
		Restart django process and visit the website.
		"""
		run('touch rnacentral/wsgi.py')
		r = requests.get(restart_url)
		if r.status_code != 200:
		    print 'Error: Website cannot be reached'

	with cd(env['rnacentral_site']):
		git_updates()
		django_updates()
		flush_memcached()
		restart_django()
