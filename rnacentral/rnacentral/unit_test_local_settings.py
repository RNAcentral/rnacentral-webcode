# File created to be used by GitLab during the execution of unit tests.
# This file is not used in production.

ENVIRONMENT = "DEV"
COMPRESS_ENABLED = False

RQ_QUEUES = {
    "default": {
        "HOST": "localhost",
        "PORT": 8051,
        "DB": 0,
        "DEFAULT_TIMEOUT": 360,
        "REMOTE_SERVER": None,
    },
}

# Public database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "pfmegrnargs",
        "USER": "reader",
        "PASSWORD": "NWDMCE5xdipIjRrp",
        "HOST": "pgsql-hhvm-001.ebi.ac.uk",  # inside campus
        "PORT": "5432",
    }
}
