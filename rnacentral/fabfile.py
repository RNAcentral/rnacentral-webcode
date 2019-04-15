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
from distutils.util import strtobool

"""
RNAcentral deployment script.

Usage:

To run locally:
    fab localhost deploy

To run remotely:
    fab -H server1,server2 production deploy

To pass parameters in:
    fab localhost deploy:quick=params.QUICK,git_branch=params.BRANCH,compress=params.COMPRESS

For more options, run `fab help`.
"""

import os
import json
import re
import requests

from fabric.api import cd, env, lcd, local, prefix, run, warn_only
from fabric.contrib import django
from simplecrypt import encrypt, decrypt

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
        env.run('git reset --hard')
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
        env.run('rm -f package-lock.json')
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

    Slack hook is encrypted with settings.SECRET_KEY by running:

    from django.conf import settings
    encrypted_slack_hook = encrypt(settings.SECRET_KEY, slack_hook)
    """
    encrypted_slack_hook = "sc\x00\x02\xe6T\xa3Wm\x1c\x91\x95\xcb3m\xbd+) \xf9\x9d1o\x86NL\xc1\xea!\x94I\xdc\x8eo\xb6\xba\x85-\xaf\x1e \xad\xfa{E\x01[+>\xba\x1d\xc6hM\xc2\xf8uLk\x11\r>\xd1\x1dg\rB2\xc5\x9b\xcd}m-$*@\xe7\xc9iJ\xee\xe3/\xba=\xa9n\xbe~c\xcd\xad\\D\xe14\x0bh\xe5\xfd2\x85Ws\xc2i\xba\xd4\xb6\x0cj\x97z\xc4\xc2\xf8\xe8\xe0)\xe3:W\xae\x92\x19+'$z\x1a\xb3\xf0\xef\x8c\xab!T=\x17\xc6\xbf-\x8e="
    slack_hook = decrypt(settings.SECRET_KEY, encrypted_slack_hook)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    requests.post(slack_hook, json.dumps({'text': message}), headers=headers)


def deploy_locally(git_branch=None, restart_url='https://rnacentral.org', quick=False, compress=True):
    """
    Run deployment locally.
    """
    slack("Starting deployment of '%s' at ves-hx-a4" % git_branch)
    git_updates(git_branch)
    if not quick:
        update_npm()
    collect_static_files()
    if compress:
        compress_static_files()
    if not quick:
        install_django_requirements()
    flush_memcached()
    restart_django(restart_url)

    if not git_branch:
        with env.cd(settings.PROJECT_PATH):
            git_branch = env.run('git rev-parse --abbrev-ref HEAD', capture=True)  # env.run == local, takes capture arg

    slack("Deployed '%s' at ves-hx-a4: <https://test.rnacentral.org|test.rnacentral.org>" % git_branch)


def deploy_remotely(git_branch=None, restart_url='https://rnacentral.org', quick=False, compress=True):
    """
    Run deployment remotely.
    """
    slack("Starting deployment of '%s' at %s" % (git_branch, env.host))
    git_updates(git_branch)

    # on PG machine npm was unable to download node_modules, so we rsync them from OY
    if not quick:
        if env.host == 'ves-pg-a4':
            cmd = 'rsync -av {path}/ {host}:{path}'.format(
                path=os.path.join(
                    settings.PROJECT_PATH,
                    'rnacentral',
                    'portal',
                    'static',
                    'node_modules'
                ),
                host='ves-pg-a4',
            )
            local(cmd)
        else:
            update_npm()

    if not quick:
        rsync_local_files()
    collect_static_files()
    if compress:
        compress_static_files()
    flush_memcached()
    restart_django(restart_url)

    if not git_branch:
        with env.cd(settings.PROJECT_PATH):
            git_branch = env.run('git rev-parse --abbrev-ref HEAD')

    slack("Deployed '%s' at %s: <https://rnacentral.org|rnacentral.org>" % (git_branch, env.host))


def deploy(git_branch=None, restart_url='https://rnacentral.org', quick=False, compress=True):
    """
    Deployment function wrapper that launches local or remote deployment
    based on the environment.
    """
    quick = strtobool(quick)
    compress = strtobool(compress)

    if env.deployment == 'remote':
        deploy_remotely(git_branch, restart_url, quick, compress)
    elif env.deployment == 'local':
        deploy_locally(git_branch, restart_url, quick, compress)
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

def fb1():
    """
    Configures environment variables for running commands on fb1, e.g.:

    fab fb1:key=/path/to/keyfile refresh_fb1
    """
    env.hosts = ['fb1-001.ebi.ac.uk']
    env.user = 'apetrov'
    env.run = run
    env.cd = cd


def pg():
    """
    Configures environment variables for running commands on pg, e.g.:

    fab pg --password=mytopsecretpassword refresh_pg
    """
    env.hosts = ['pg-001.ebi.ac.uk']
    env.user = 'apetrov'
    env.run = run
    env.cd = cd


def ebi_cli():
    """
    Configures environment variables for running commands on ebi-cli-001, e.g.:

    fab pg --password=mytopsecretpassword refresh_dev
    """
    env.hosts = ['ebi-cli.ebi.ac.uk']
    env.user = 'burkov'
    env.run = run
    env.cd = cd


def refresh_fb1():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_create_snapshot.sh -s pgsql-hxvm-038.ebi.ac.uk | tail -1")
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvm-010.ebi.ac.uk -S '%s'" % snapshot)

    slack("Refreshed FB1 database from '%s' snapshot" % snapshot)


def push_replication():
    """Login to the FB machine and push replication of HX snapshot from it to HH"""
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_push_replication.sh -s pgsql-hxvm-038.ebi.ac.uk")


def refresh_pg():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_list_snapshots.sh -d pgsql-dlvmpub1-010.ebi.ac.uk | tail -1")
    # bash curses about absence of /home directory, thus we have to filter out snapshot
    snapshot = re.search("\d\d\d\d\-\d\d\-\d\d\s\d\d\:\d\d$", snapshot).group(0)  # e.g. 2018-06-26 11:16
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvmpub1-010.ebi.ac.uk -S '%s'" % snapshot)

    slack("Refreshed PG database from '%s' snapshot" % snapshot)


def refresh_dev():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_list_snapshots.sh -d pgsql-dlvm-008.ebi.ac.uk | tail -1")
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvm-008.ebi.ac.uk -S '%s'" % snapshot)

    slack("Refreshed DEV database from '%s' snapshot" % snapshot)


def refresh_tst():
    snapshot = env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_list_snapshots.sh -d pgsql-dlvm-009.ebi.ac.uk | tail -1")
    env.run("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvm-009.ebi.ac.uk -S '%s'" % snapshot)

    slack("Refreshed TST database from '%s' snapshot" % snapshot)
