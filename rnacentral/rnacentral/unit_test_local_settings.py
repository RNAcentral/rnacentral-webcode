# File created to be used by GitHub Action during the execution of unit tests.
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
