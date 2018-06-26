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

from __future__ import print_function

"""
RNAcentral deployment script.

Usage:

To run locally:
    fab localhost deploy

To run remotely:
    fab -H server1,server2 production deploy

For more options, run `fab help`.
"""

import os
import json
import re
import requests

from fabric.api import cd, env, lcd, local, prefix, run, warn_only
from fabric.contrib import django

# load Django settings
django.settings_module('rnacentral.settings')
from django.conf import settings
print(settings)  # this is a lazy object and should be evaluated to be used

COMMANDS = {
    'set_environment': 'source rnacentral/scripts/env.sh',
    'activate_virtualenv': 'source ../local/virtualenvs/RNAcentral/bin/activate', # pylint: disable=C0301
}

env.deployment = None


def production():
    """
    Enable remote execution of tasks.
    """
    env.run = run
    env.cd = cd
    env.deployment = 'remote'


def localhost():
    """
    Enable local execution of tasks.
    Load local versions of Fabric functions into the shared environment.
    """
    env.run = local
    env.cd = lcd
    env.deployment = 'local'


def git_updates(git_branch=None):
    """
    Perform git updates.
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


def update_npm():
    """
    Navigate to the folder with `package.json` and run npm update to install
    static content dependencies.
    """
    path = os.path.join(settings.PROJECT_PATH, 'rnacentral', 'portal', 'static')
    with env.cd(path):
        env.run('npm update --loglevel info')


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


def create_sitemaps():
    """
    Create sitemaps cache in sitemaps folder.
    """
    with env.cd(settings.PROJECT_PATH), prefix(COMMANDS['set_environment']), \
         prefix(COMMANDS['activate_virtualenv']):
        env.run('rm rnacentral/sitemaps/*')
        env.run('python rnacentral/manage.py create_sitemaps')
        slack("Created sitemaps at ves-oy-a4")


def rsync_sitemaps(dry_run=None, remote_host='ves-pg-a4'):
    """
    Copy cached sitemaps from local folder to remote one.
    """
    sitemaps_path = os.path.join(settings.PROJECT_PATH, 'rnacentral', 'sitemaps')

    cmd = 'rsync -avi{dry_run} --delete {src}/ {remote_host}:{dst}'.format(
        src=sitemaps_path,
        dst=sitemaps_path,
        remote_host=remote_host,
        dry_run='n' if dry_run else '',
    )
    local(cmd)
    slack("Rsynced sitemaps to %s" % remote_host)


def flush_memcached():
    """
    Delete all cached data.
    """
    (host, port) = settings.CACHES['default']['LOCATION'].split(':')
    cmd = 'echo flush_all | nc {host} {port} -vv'.format(host=host, port=port)
    with warn_only():
        env.run(cmd)


def start_supervisor():
    """
    Start supervisord and memcached on production machine.
    """
    with env.cd(settings.PROJECT_PATH), prefix(COMMANDS['set_environment']), \
         prefix(COMMANDS['activate_virtualenv']):
        env.run('supervisord -c supervisor/supervisor.conf')
        env.run('supervisorctl -c supervisor/supervisor.conf start memcached')


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


def slack(message):
    """
    Send message to slack RNAcentral channel.
    """
    slack_hook = 'https://hooks.slack.com/services/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'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    requests.post(slack_hook, json.dumps({'text': message}), headers=headers)


def deploy_locally(git_branch=None, restart_url='http://rnacentral.org', quick=False):
    """
    Run deployment locally.
    """
    git_updates(git_branch)
    update_npm()
    collect_static_files()
    compress_static_files()
    if not quick:
        install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

    if not git_branch:
        with env.cd(settings.PROJECT_PATH):
            git_branch = env.run('git rev-parse --abbrev-ref HEAD', capture=True)  # env.run == local, takes capture arg

    slack("Deployed '%s' at ves-hx-a4: <http://test.rnacentral.org|test.rnacentral.org>" % git_branch)


def deploy_remotely(git_branch=None, restart_url='http://rnacentral.org', quick=False):
    """
    Run deployment remotely.
    """
    git_updates(git_branch)
    update_npm()
    if not quick:
        rsync_local_files()
    collect_static_files()
    compress_static_files()
    flush_memcached()
    restart_django(restart_url)

    if not git_branch:
        with env.cd(settings.PROJECT_PATH):
            git_branch = env.run('git rev-parse --abbrev-ref HEAD')
    slack("Deployed '%s' at %s: <http://rnacentral.org|rnacentral.org>" % (git_branch, env.host))


def deploy(git_branch=None, restart_url='http://rnacentral.org', quick=False):
    """
    Deployment function wrapper that launches local or remote deployment
    based on the environment.
    """
    if env.deployment == 'remote':
        deploy_remotely(git_branch, restart_url, quick)
    elif env.deployment == 'local':
        deploy_locally(git_branch, restart_url, quick)
    else:
        print('Check usage')


def test(base_url='http://localhost:8000/'):
    """
    Single entry point for all tests.
    """
    with env.cd(settings.PROJECT_PATH):
        # env.run('python rnacentral/apiv1/tests.py --base_url=%s' % base_url)
        env.run('python rnacentral/portal/tests/selenium_tests.py --base_url %s --driver=phantomjs' % base_url)  # pylint: disable=C0301
        env.run('python rnacentral/apiv1/search/sequence/tests.py --base_url %s' % base_url)  # pylint: disable=C0301


# VDBS refresh-related code

def fb1(key):
    """
    Configures environment variables for running commands on fb1, e.g.:

    fab fb1:key=/path/to/keyfile refresh_fb1
    """
    env.hosts = ['fb1-001.ebi.ac.uk']
    env.user = 'burkov'
    env.run = run
    env.cd = cd
    env.key_filename = key


def pg(password):
    """
    Configures environment variables for running commands on pg, e.g.:

    fab pg:password=mytopsecretpassword refresh_pg
    """
    env.hosts = ['pg-001.ebi.ac.uk']
    env.user = 'burkov'
    env.password = password
    env.run = run
    env.cd = cd


def refresh_fb1():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_create_snapshot.sh -s pgsql-hxvm-038.ebi.ac.uk | tail -1")
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvm-010.ebi.ac.uk -S '%s'" % snapshot)
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_push_replication.sh -s pgsql-hxvm-038.ebi.ac.uk")


def refresh_pg():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_list_snapshots.sh -d pgsql-dlvmpub1-010.ebi.ac.uk | tail -1")
    # bash curses about absence of /home directory, thus we have to filter out snapshot
    snapshot = re.search("\d\d\d\d\-\d\d\-\d\d\s\d\d\:\d\d$", snapshot).group(0)  # e.g. 2018-06-26 11:16
    print(snapshot)
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvmpub1-010.ebi.ac.uk -S '%s'" % snapshot)
