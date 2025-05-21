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
            "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
            "LOCATION": "memcached:11211",
        },
        "sitemaps": {
            "BACKEND": "rnacentral.utils.cache.SitemapsCache",
            "LOCATION": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rnacentral', 'sitemaps')
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
            "CONN_MAX_AGE": 0
        }
    }
	EOF
	sed -i "3 a DEBUG = ${DJANGO_DEBUG}" "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
	chown -R rnacentral "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
fi


echo "INFO: Collecting static files..."
python "${RNACENTRAL_HOME}"/rnacentral/manage.py collectstatic --noinput


# Run django compressor
echo "INFO: Running django compress"
python "${RNACENTRAL_HOME}"/rnacentral/manage.py compress

exec "$@"
