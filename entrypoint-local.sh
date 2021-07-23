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

# Add debug_toolbar info
if ! grep -q debug_toolbar "${RNACENTRAL_HOME}"/rnacentral/rnacentral/urls.py; then
  sed -i "13 a import debug_toolbar" "${RNACENTRAL_HOME}"/rnacentral/rnacentral/urls.py ; \
  sed -i "31 a \ \ \ \ url(r'^__debug__/', include(debug_toolbar.urls))," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/urls.py ; \
  sed -i "129 a \ \ \ \ 'debug_toolbar.middleware.DebugToolbarMiddleware'," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/settings.py ; \
  sed -i "188 a \ \ \ \ 'debug_toolbar'," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/settings.py ; \
fi

# Create symbolic link to node_modules directory
if [ ! -d "${RNACENTRAL_HOME}"/rnacentral/portal/static/node_modules ]
then
	echo "INFO: Creating symbolic link to node_modules directory"
	ln -s /srv/rnacentral/node_modules "${RNACENTRAL_HOME}"/rnacentral/portal/static
fi

# Add local_settings file
echo "INFO: Creating RNAcentral local_settings.py file"
cat <<-EOF > "${RNACENTRAL_HOME}"/rnacentral/rnacentral/local_settings.py
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

exec "$@"