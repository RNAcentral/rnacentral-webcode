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

from django.conf import settings

import psycopg2


def psycopg2_string():
    """
    Generates a connection string for psycopg2
    """
    return 'dbname={db} user={user} password={password} host={host} port={port}'.format(
        db=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
    )

def get_db_connection():
    """
    Open a database connection.
    Should be used in situations where @contextmanager connection doesn't work.
    For example, loading a new release should not be done with @contextmanager
    because it wraps all work in a giant database transaction
    that is likely to crash.
    """
    conn = psycopg2.connect(psycopg2_string())
    conn.set_session(autocommit=False)
    conn.set_isolation_level(0)
    return conn
