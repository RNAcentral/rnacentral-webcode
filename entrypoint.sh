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

# Supervisor
SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# Entrypoint variable
RNACENTRAL_PROJECT_PATH="${RNACENTRAL_HOME}/rnacentral-webcode/rnacentral"

# Add local_settings file
if [ -f "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py ]
then
	echo "INFO: RNAcentral local_settings.py file already provisioned"
else
	echo "INFO: Creating RNAcentral local_settings.py file"
	cat <<-EOF > "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py
		from utils import get_environment
		SECRET_KEY = "$SECRET_KEY"
		DEBUG = True
		ENVIRONMENT = get_environment()
		INTERNAL_IPS = ('127.0.0.1', '192.168.99.1')
		COMPRESS_ENABLED = False
		RQ_QUEUES = {
        "default": {
            "HOST": "192.168.1.3",
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
	chown -R nobody "${RNACENTRAL_PROJECT_PATH}"/rnacentral/local_settings.py
fi

# Supervisor setup
echo "INFO: Creating Supervisord configuration file"
mkdir -p "$SUPERVISOR_CONF_DIR"
cat <<-EOF > "${SUPERVISOR_CONF_DIR}"/supervisord.conf
[supervisord]
logfile=/var/log/supervisord.log
logfile_maxbytes=50MB
logfile_backups=2
loglevel=info
nodaemon=true

[program:rqworkers]
command=python $RNACENTRAL_HOME/rnacentral-webcode/rnacentral/manage.py rqworker
directory=$RNACENTRAL_HOME/rnacentral-webcode/rnacentral
numprocs=2
process_name=%(program_name)s_%(process_num)s
autorestart=true
autostart=true
stderr_logfile=/var/log/rqworkers.err.log
stdout_logfile=/var/log/rqworkers.out.log

[program:rnacentral]
command=python $RNACENTRAL_HOME/rnacentral-webcode/rnacentral/manage.py runserver 0.0.0.0:8000
user=nobody
autostart=true
autorestart=true
stderr_logfile=/var/log/rnacentral.err.log
stdout_logfile=/var/log/rnacentral.out.log
environment=HOME="$RNACENTRAL_HOME"
EOF

exec "$@"