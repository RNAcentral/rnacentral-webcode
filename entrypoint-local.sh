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

# Add debug_toolbar info
if ! grep -q debug_toolbar "${RNACENTRAL_HOME}"/rnacentral/urls.py; then
  sed -i "13 a import debug_toolbar" "${RNACENTRAL_HOME}"/rnacentral/urls.py ; \
  sed -i "31 a \ \ \ \ url(r'^__debug__/', include(debug_toolbar.urls))," "${RNACENTRAL_HOME}"/rnacentral/urls.py ; \
  sed -i "129 a \ \ \ \ 'debug_toolbar.middleware.DebugToolbarMiddleware'," "${RNACENTRAL_HOME}"/rnacentral/settings.py ; \
  sed -i "188 a \ \ \ \ 'debug_toolbar'," "${RNACENTRAL_HOME}"/rnacentral/settings.py ; \
fi

# Add local_settings file
if [ -f "${RNACENTRAL_HOME}"/rnacentral/local_settings.py ]
then
	echo "INFO: RNAcentral local_settings.py file already provisioned"
else
	echo "INFO: Creating RNAcentral local_settings.py file"
	cat <<-EOF > "${RNACENTRAL_HOME}"/rnacentral/local_settings.py
		import os
		from .utils import get_environment
		SECRET_KEY = "$SECRET_KEY"
		DEBUG = True
		EBI_SEARCH_ENDPOINT = "$EBI_SEARCH_ENDPOINT"
		ENVIRONMENT = get_environment()
		INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')
		DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG}
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
		command=python $RNACENTRAL_HOME/manage.py rqworker
		directory=$RNACENTRAL_HOME/rnacentral
		numprocs=1
		process_name=%(program_name)s_%(process_num)s
		autorestart=true
		autostart=true
		stderr_logfile=${LOGS}/rqworkers.err.log
		stdout_logfile=${LOGS}/rqworkers.out.log
	EOF
fi

exec "$@"