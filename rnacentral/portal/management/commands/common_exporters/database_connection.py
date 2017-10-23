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

import random
from contextlib import contextmanager

import psycopg2

from django.conf import settings


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
    """
    return psycopg2.connect(psycopg2_string())

@contextmanager
def connection():
    """
    Get a database connection.
    """
    conn = psycopg2.connect(psycopg2_string())
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def cursor():
    """
    Create a database cursor.
    """
    with connection() as conn:
        cursor_name = 'rnacentral-server-side-%i' % random.randint(1, 1000)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor,
                          name=cursor_name)
        try:
            yield cur
        finally:
            cur.close()
