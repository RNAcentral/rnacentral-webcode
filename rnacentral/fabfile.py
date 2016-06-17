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
from fabric.api import cd, env, lcd, local, prefix, run, warn_only
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
    with warn_only():
        env.run(cmd)

def restart_django(restart_url=None):
    """
    Restart django process and visit the website.
    """
    with env.cd(settings.PROJECT_PATH):
        env.run('touch rnacentral/rnacentral/wsgi.py')
        if restart_url:
            requests.get(restart_url)

def rsync_local_files(dry_run=None):
    """
    Rsync local files to production.
    """
    local_path = os.path.join(os.path.dirname(settings.PROJECT_PATH), 'local')
    cmd = 'rsync -av{dry_run} {src}/ {host}:{dst}'.format(
        src=local_path,
        host=env.host,
        dst=local_path,
        dry_run='n' if dry_run else '',
    )
    local(cmd)

def deploy(git_branch=None, restart_url='http://rnacentral.org', quick=False):
    """
    Run deployment locally.
    """
    git_updates(git_branch)
    collect_static_files()
    compress_static_files()
    if not quick:
        install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

def deploy_remotely(git_branch=None, restart_url='http://rnacentral.org'):
    """
    Run deployment remotely.
    """
    git_updates(git_branch)
    collect_static_files()
    compress_static_files()
    flush_memcached()
    restart_django(restart_url)
    rsync_local_files()

def test(base_url='http://localhost:8000/'):
    """
    Single entry point for all tests.
    """
    with env.cd(settings.PROJECT_PATH):
        env.run('python rnacentral/apiv1/tests.py --base_url=%s' % base_url)
        env.run('python rnacentral/portal/tests/selenium_tests.py --base_url %s --driver=phantomjs' % base_url) # pylint: disable=C0301
        env.run('python rnacentral/apiv1/search/sequence/tests.py --base_url %s' % base_url) # pylint: disable=C0301
