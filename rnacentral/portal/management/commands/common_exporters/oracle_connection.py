"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

import cx_Oracle
from django.conf import settings


class OracleConnection(object):
    """
    Manually connect to the Oracle database using cx_Oracle and Django settings.
    """

    def __init__(self):
        """
        Declare internal variables.
        """
        self.connection = None
        self.cursor = None

    def get_connection(self, db_url=None):
        """
        Get Oracle connection using database details from Django settings.
        """
        if not db_url:
            db_url = '{username}/{password}@{db_name}'.format(
                username=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                db_name=settings.DATABASES['default']['NAME'])
        self.connection = cx_Oracle.Connection(db_url)

    def get_cursor(self):
        """
        Get Oracle cursor.
        """
        if not self.connection:
            self.get_connection()
        self.cursor = self.connection.cursor()
        self.cursor.arraysize = 128

    def close_connection(self):
        """
        Close Oracle connection.
        """
        self.connection.close()

    def row_to_dict(self, row):
        """
        Convert Oracle results from tuples to dicts to improve code readability.
        """
        description = [d[0].lower() for d in self.cursor.description]
        return dict(zip(description, row))
