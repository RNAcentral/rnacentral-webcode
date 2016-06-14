"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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

"""
RNAcentral deployment script using Fabric.

Usage:

To run locally:
    fab localhost <task>
Example:
    fab localhost deploy

To run remotely:
    fab -H user@server1,user@server2 <task>
Example:
    fab -H user@server1,user@server2 deploy_remotely

For more options, run `fab help`.
"""

import os
import requests
from fabric.api import cd, env, lcd, local, prefix, run
from fabric.contrib import django

# load Django settings
django.settings_module('rnacentral.settings')
from django.conf import settings
print settings # this is a lazy object and should be evaluated to be used

COMMANDS = {
    'set_environment': 'source rnacentral/scripts/env.sh',
    'activate_virtualenv': 'source ../local/virtualenvs/RNAcentral/bin/activate', # pylint: disable=C0301
}

# set default values in the shared environment
env.run = run
env.cd = cd

def localhost():
    """
    Enable local execution of tasks.
    Load local versions of Fabric functions into the shared environment.
    """
    env.run = local
    env.cd = lcd

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
               "--exclude '*.pid' {host}:{dst}").format(host=env.host,
                src=parent_dir, dst=parent_parent_dir)
        local(cmd)

def git_updates(git_branch=None):
    """
    Perform git updates, but only on the test server because the production
    servers must use rsync to preserve file modification time.
    """
    with env.cd(settings.PROJECT_PATH):
        if git_branch:
            env.run('git checkout {branch}'.format(branch=git_branch))
        env.run('git pull')
        env.run('git submodule update')

def install_django_requirements():
    """
    Run pip install.
    """
    with env.cd(settings.PROJECT_PATH), prefix(COMMANDS['set_environment']), \
         prefix(COMMANDS['activate_virtualenv']):
        env.run('pip install --upgrade -r rnacentral/requirements.txt')

def rsync_static_files():
    """
    Rsync static files from test to production.
    This is done to synchronize modification times of css files.
    """
    with lcd(env['static_files']):
        parent_dir = os.path.abspath(os.path.join(env['static_files'], os.pardir)) # pylint: disable=C0301
        cmd = 'rsync -av {src} {host}:{dst}'.format(host=env.host,
            src=env['static_files'], dst=parent_dir)
        local(cmd)

def collect_static_files():
    """
    Run django `collectstatic` command.
    """
    with env.cd(settings.PROJECT_PATH), prefix(COMMANDS['set_environment']), \
         prefix(COMMANDS['activate_virtualenv']):    
        env.run('python rnacentral/manage.py collectstatic --noinput')

def compress_static_files():
    """
    Run django compressor.
    """
    with env.cd(settings.PROJECT_PATH), prefix(COMMANDS['set_environment']), \
         prefix(COMMANDS['activate_virtualenv']):
        env.run('python rnacentral/manage.py compress')

def flush_memcached():
    """
    Delete all cached data.
    """
    (host, port) = settings.CACHES['default']['LOCATION'].split(':')
    cmd = 'echo flush_all | nc {host} {port} -vv'.format(host=host, port=port)
    env.run(cmd)

def restart_django(restart_url=None):
    """
    Restart django process and visit the website.
    """
    with env.cd(settings.PROJECT_PATH):
        env.run('touch rnacentral/rnacentral/wsgi.py')
        if restart_url:
            requests.get(restart_url)

def deploy(git_branch=None, restart_url='http://rnacentral.org'):
    """
    Run deployment locally.
    """
    git_updates(git_branch)
    collect_static_files()
    install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

def deploy_remotely(restart_url='http://rnacentral.org'):
    """
    Run deployment remotely.
    """
    rsync_git_repo()
    rsync_static_files()
    install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

def test(base_url='http://localhost:8000/'):
    """
    Single entry point for all tests.
    """
    with env.cd(settings.PROJECT_PATH):
        env.run('python rnacentral/apiv1/tests.py --base_url=%s' % base_url)
        env.run('python rnacentral/portal/tests/selenium_tests.py --base_url %s --driver=phantomjs' % base_url) # pylint: disable=C0301
        env.run('python rnacentral/apiv1/search/sequence/tests.py --base_url %s' % base_url) # pylint: disable=C0301
