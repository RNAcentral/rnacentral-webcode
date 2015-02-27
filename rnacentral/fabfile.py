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

import os.path
import requests
from fabric.api import *

"""
Fabric deployment script

Usage:

fab -H user@server1,user@server2 -c /path/to/fab.cfg deploy:git_branch=my_git_branch:website_url=my_website_url

where:

* -H - list of host names
* -c - path to the configuration file
* deploy - name of the task to run
* git_branch - git branch to deploy (dev by default)
* website_url - which url should be used to jumpstart the server

fab.cfg template:

rnacentral_site=/path/to/manage.py
activate=source /path/to/virtualenvs/RNAcentral/bin/activate
ld_library_path=export LD_LIBRARY_PATH=/path/to/oracle/libraries/:$LD_LIBRARY_PATH
oracle_home=export ORACLE_HOME=/path/to/oracle/libraries/
static_files=/path/to/static/files
"""

def rsync_git_repo():
    """
    Use rsync to sync git repositories. This is required for django-compressor
    to generate the same static files, which rely on file modification time.
    """
    with lcd(env['rnacentral_site']):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
        parent_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
        cmd = ("rsync -av {src} --exclude 'rnacentral/local_settings.py' " + \
               "--exclude '*.log' --exclude '*.pyc' --exclude 'dump.rdb' " + \
               "{host}:{dst}").format(host=env.host, src=parent_dir,
            dst=parent_parent_dir)
        local(cmd)

def git_updates(git_branch):
    """
    Perform git updates, but only on the test server because the production
    servers must use rsync to preserve file modification time.
    """
    with cd(env['rnacentral_site']):
        # make sure we are on the right branch
        run('git checkout %s' % git_branch)
        # get latest changes
        run('git pull')
        # update git submodules
        this_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
        with cd(parent_dir):
            run('git submodule update')

def install_django_requirements():
    """
    * activate virtual environment
    * set Oracle variables
    * install all python requirements
    """
    with cd(env['rnacentral_site']), prefix(env['activate']), prefix(env['ld_library_path']), prefix(env['oracle_home']):
        run('pip install --upgrade -r requirements.txt')

def rsync_static_files():
    """
    Rsync static files from the test to production.
    This is done to synchronize modification times of css files.
    """
    with lcd(env['static_files']):
        parent_dir = os.path.abspath(os.path.join(env['static_files'], os.pardir))
        cmd = 'rsync -av {src} {host}:{dst}'.format(host=env.host,
            src=env['static_files'], dst=parent_dir)
        local(cmd)

def collect_static_files():
    """
    * activate virtual environment
    * set Oracle variables
    * move static files to the deployment location
    """
    with cd(env['rnacentral_site']), prefix(env['activate']), prefix(env['ld_library_path']), prefix(env['oracle_home']):
        with prefix('source ../scripts/env.sh'):
            run('python manage.py collectstatic --noinput')

def flush_memcached():
    """
    Delete all cached data.
    """
    with cd(env['rnacentral_site']), settings(warn_only=True):
            run('echo "flush_all" | nc -U rnacentral/memcached.sock')

def restart_django(restart_url):
    """
    Restart django process and visit the website.
    """
    with cd(env['rnacentral_site']), prefix('source ../scripts/env.sh'):
        run('touch rnacentral/wsgi.py')
        r = requests.get(restart_url)
        if r.status_code != 200:
            print 'Error: Website cannot be reached'

def deploy(git_branch='dev', restart_url="http://rnacentral.org"):
    """
    Deploy to a server.
    """
    if env.host == 'ves-hx-61':
        # will run only when deploying to test servers
        git_updates(git_branch)
        collect_static_files()
    else:
        # will run only when deploying to production servers
        rsync_git_repo()
        rsync_static_files()
    install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

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
