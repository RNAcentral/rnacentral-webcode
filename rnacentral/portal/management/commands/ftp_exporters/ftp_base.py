"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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
import cx_Oracle
import logging
import os
import re
import subprocess
import sys


class FtpBase(object):
    """
    Base class for FTP export helper classes.
    """

    def __init__(self, destination='', test=False):
    	"""
        Set common variables.
    	"""
        self.destination = destination
        self.test = test # boolean indicating whether to export all data or the first `self.entries`.
        self.test_entries = 100 # number of entries to process when --test=True
        self.examples = 5 # number of entries to write to the example files
        self.connection = None # Oracle connection
        self.cursor = None # Oracle cursor
        self.filehandles = {}
        self.filenames = {}
        self.log = 'logfile.txt'

    #########################
    # Files and directories #
    #########################

    def get_output_filename(self, filename, parent_dir=''):
        """
        Get full path to the file `filename`
        located either in `self.destination` or `parent_dir`.
        """
        if parent_dir:
            return os.path.join(parent_dir, filename)
        else:
            return os.path.join(self.destination, filename)

    def get_filenames_and_filehandles(self, names, destination=''):
        """
        Get all required filenames and filehandles.

        names = {
            'file_nickname': 'file_full_name',
            'readme': 'readme.txt',
        }

        destination = 'path/to/output/files' # optional
        """
        # reset the dictionaries
        self.filehandles = {}
        self.filenames = {}
        # use self.destination by default
        if not destination:
            destination = self.destination
        for key, value in names.iteritems():
            value = self.get_output_filename(value, parent_dir=destination)
            self.filenames[key] = value
            self.filehandles[key] = open(value, 'w')

    def make_subdirectory(self, parent_dir, child_dir):
        """
        Create a subdirectory child_dir in directory parent_dir.
        """
        new_folder = os.path.join(parent_dir, child_dir)
        if not os.path.exists(new_folder):
            os.mkdir(new_folder)
        return new_folder

    def clean_up(self):
        """
        * close all filehandles
        * gzip and delete all files except for examples and readme
        * close Oracle connection.
        """
        for filename, filepath in self.filenames.iteritems():
            self.filehandles[filename].close()
            if 'example' not in filename and 'readme' not in filename:
                self.gzip_file(filepath)
                os.remove(filepath)
        self.close_connection()

    def gzip_file(self, filename):
        """
        Compress a given file using gzip, return the compressed file name.
        """
        gzipped_filename = '%s.gz' % filename
        cmd = 'gzip < %s > %s' % (filename, gzipped_filename)
        logging.info('Compressing file %s' % filename)
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            logging.info('\File compressed, new file %s' % gzipped_filename)
            return gzipped_filename
        else:
            logging.info('Compressing failed, no file created')
            return ''

    ##################
    # Oracle helpers #
    ##################

    def get_connection(self):
        """
        Get Oracle connection using database details from Django settings.
        """
        db_url = '{username}/{password}@{db_name}'.format(username=settings.DATABASES['default']['USER'],
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
        try:
            self.connection.close()
        except:
            logging.critical('Could not close Oracle connection.')

    def row_to_dict(self, row):
        """
        Convert Oracle results from tuples to dicts to improve code readability.
        """
        description = [d[0].lower() for d in self.cursor.description]
        return dict(zip(description, row))

    def log_oracle_error(self, oracle_exception):
        """
        """
        error, = oracle_exception.args
        logging.critical('Oracle error code: %s' % error.code)
        logging.critical('Oracle message: %s' % error.message)

    ##################
    # Data retrieval #
    ##################

    def get_xrefs_with_genomic_coordinates(self):
        """
        Get RNA sequences with genomic coordinates.
        """
        xrefs = Xref.objects.filter(db_id=5).\
                             select_related('accession', 'accession__assembly',
                                            'accession__assembly__chromosome').\
                             all()
        if self.test:
            return xrefs[:100]
        return xrefs

    ########
    # Misc #
    ########

    def format_docstring(self, text):
        """
        Prepare docstring to be saved in a text file.
        """
        text = re.sub(r'^\s+', '', text)
        text = re.sub(r'\n +', '\n', text)
        return text

    def start_logging(self):
        """
        Overwrites the old log file.
        """
        filename = os.path.join(os.getcwd(), self.log)
        logging.basicConfig(filename=filename,
                            level=logging.DEBUG,
                            format='%(levelname)s:%(message)s',
                            filemode='w')
        print 'Log file %s' % filename
