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
SECRET_KEY=${SECRET_KEY:-'your_secret_key'}
DJANGO_DEBUG=${DJANGO_DEBUG:-'False'}
S3_HOST=${S3_HOST}
S3_KEY=${S3_KEY}
S3_SECRET=${S3_SECRET}

# Supervisor
SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/srv/rnacentral/supervisor"}

# Entrypoint variable
RNACENTRAL_PROJECT_PATH="${RNACENTRAL_HOME}/rnacentral-webcode/rnacentral"
LOGS="${RNACENTRAL_HOME}/log"

# Add local_settings file
if [ -f "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py ]
then
	echo "INFO: RNAcentral local_settings.py file already provisioned"
else
	echo "INFO: Creating RNAcentral local_settings.py file"
	cat <<-EOF > "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py
		import os
		from .utils import get_environment
		SECRET_KEY = "$SECRET_KEY"
		ENVIRONMENT = get_environment()
		INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')
		COMPRESS_ENABLED = False
		S3_SERVER = {
        "HOST": "$S3_HOST",
        "KEY": "$S3_KEY",
        "SECRET": "$S3_SECRET",
        "BUCKET": "ebi-rnacentral",
    }
		CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached",
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
	sed -i "3 a DEBUG = ${DJANGO_DEBUG}" "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py
	chown -R rnacentral "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py
fi

# Supervisor setup
if [ -f "${SUPERVISOR_CONF_DIR}"/supervisord.conf ]
then
	echo "INFO: Supervisord configuration file already provisioned"
else
	echo "INFO: Creating Supervisord configuration file"
	mkdir -p "$SUPERVISOR_CONF_DIR"
	mkdir -p "${LOGS}"
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
		command=python $RNACENTRAL_HOME/rnacentral-webcode/rnacentral/manage.py rqworker
		directory=$RNACENTRAL_HOME/rnacentral-webcode/rnacentral
		numprocs=4
		process_name=%(program_name)s_%(process_num)s
		autorestart=true
		autostart=true
		stderr_logfile=${LOGS}/rqworkers.err.log
		stdout_logfile=${LOGS}/rqworkers.out.log

		[program:rnacentral]
		command=$RNACENTRAL_HOME/.local/bin/gunicorn --chdir $RNACENTRAL_HOME/rnacentral-webcode/rnacentral --bind 0.0.0.0:8000 rnacentral.wsgi:application
		user=rnacentral
		autostart=true
		autorestart=true
		stderr_logfile=${LOGS}/rnacentral.err.log
		stdout_logfile=${LOGS}/rnacentral.out.log
		environment=HOME="$RNACENTRAL_HOME"
	EOF
fi

exec "$@"