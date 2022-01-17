#!/bin/sh
set -e

# SYSTEM OPTIONS (set on Docker build)
RNACENTRAL_HOME=$RNACENTRAL_HOME

# External database settings
DB_HOST=${DB_HOST:-'hh-pgsql-public.ebi.ac.uk'}
DB_NAME=${DB_NAME:-'pfmegrnargs'}
DB_USER=${DB_USER:-'reader'}
DB_PORT=${DB_PORT:-'5432'}
DB_PASSWORD=${DB_PASSWORD:-'NWDMCE5xdipIjRrp'}

# RNAcentral specific settings
SECRET_KEY=${SECRET_KEY:-$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')}
DJANGO_DEBUG=${DJANGO_DEBUG:-'False'}
EBI_SEARCH_ENDPOINT=${EBI_SEARCH_ENDPOINT:-'http://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral'}
S3_HOST=${S3_HOST}
S3_KEY=${S3_KEY}
S3_SECRET=${S3_SECRET}

# Supervisor
SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/srv/rnacentral/supervisor"}

# Entrypoint variable
LOGS=/srv/rnacentral/log

# Add local_settings file
if [ -f "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py ]
then
	echo "INFO: RNAcentral local_settings.py file already provisioned"
else
	echo "INFO: Creating RNAcentral local_settings.py file"
	cat <<-EOF > "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
		import os
		from .utils import get_environment
		SECRET_KEY = "$SECRET_KEY"
		EBI_SEARCH_ENDPOINT = "$EBI_SEARCH_ENDPOINT"
		ENVIRONMENT = get_environment()
		INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')
		DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG}
		S3_SERVER = {
        "HOST": "$S3_HOST",
        "KEY": "$S3_KEY",
        "SECRET": "$S3_SECRET",
        "BUCKET": "ebi-rnacentral",
    }
		CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached:11211",
        },
        "sitemaps": {
            "BACKEND": "rnacentral.utils.cache.SitemapsCache",
            "LOCATION": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rnacentral', 'sitemaps')
        }
    }
		RQ_QUEUES = {
        "default": {
            "HOST": "redis",
            "PORT": 8051,
            "DB": 0,
            "DEFAULT_TIMEOUT": 360,
            "REMOTE_SERVER": None,
        }
    }
		DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "$DB_NAME",
            "USER": "$DB_USER",
            "PASSWORD": "$DB_PASSWORD",
            "HOST": "$DB_HOST",
            "PORT": "$DB_PORT",
        }
    }
	EOF
	sed -i "3 a DEBUG = ${DJANGO_DEBUG}" "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
	chown -R rnacentral "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
fi

# Add local_settings file in the export app
# /srv/rnacentral/fasta and /srv/rnacentral/export are k8 volumes in prod
if [ -f "${RNACENTRAL_HOME}"/rnacentral/export/local_settings.py ]
then
	echo "INFO: The local_settings.py file for the export app has already been provisioned"
else
	echo "INFO: Creating local_settings.py file for the export app"
	cat <<-EOF > "${RNACENTRAL_HOME}"/rnacentral/export/local_settings.py
		FASTA_DB = '/srv/rnacentral/fasta/rnacentral_species_specific_ids.fasta'
		EXPORT_RESULTS_DIR = '/srv/rnacentral/export'
	EOF
	chown rnacentral "${RNACENTRAL_HOME}"/rnacentral/export/local_settings.py
fi

# Supervisor setup
if [ -f "${SUPERVISOR_CONF_DIR}"/supervisord.conf ]
then
	echo "INFO: Supervisord configuration file already provisioned"
else
	echo "INFO: Creating Supervisord configuration file"
	cat <<-EOF > "${SUPERVISOR_CONF_DIR}"/supervisord.conf
		[supervisord]
		pidfile=${SUPERVISOR_CONF_DIR}/supervisord.pid
		logfile=${LOGS}/supervisord.log
		user=rnacentral
		logfile_maxbytes=50MB
		logfile_backups=2
		loglevel=info
		nodaemon=true

		[program:rqworkers]
		command=python $RNACENTRAL_HOME/rnacentral/manage.py rqworker
		directory=$RNACENTRAL_HOME/rnacentral
		numprocs=4
		process_name=%(program_name)s_%(process_num)s
		autorestart=true
		autostart=true
		stderr_logfile=${LOGS}/rqworkers.err.log
		stdout_logfile=${LOGS}/rqworkers.out.log

		[program:rnacentral]
		command=gunicorn --chdir $RNACENTRAL_HOME/rnacentral --bind 0.0.0.0:8000 rnacentral.wsgi:application
		user=rnacentral
		autostart=true
		autorestart=true
		stderr_logfile=${LOGS}/rnacentral.err.log
		stdout_logfile=${LOGS}/rnacentral.out.log
		environment=HOME="$RNACENTRAL_HOME"
	EOF
	chown -R rnacentral "${SUPERVISOR_CONF_DIR}"/supervisord.conf
fi

# Run create_sitemaps
echo "INFO: Creating sitemaps"
python "${RNACENTRAL_HOME}"/rnacentral/manage.py create_sitemaps

# Run collectstatic
echo "INFO: Copying the static files"
python "${RNACENTRAL_HOME}"/rnacentral/manage.py collectstatic --noinput

# Run django compressor
echo "INFO: Running django compress"
python "${RNACENTRAL_HOME}"/rnacentral/manage.py compress

exec "$@"
