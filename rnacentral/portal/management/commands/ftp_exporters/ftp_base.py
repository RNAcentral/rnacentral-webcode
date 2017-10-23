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

import os
import logging
import re
import subprocess
import time

from django.contrib.humanize.templatetags.humanize import intcomma

from portal.models import Rna, Database, Xref


class FtpBase(object):
    """
    Base class for FTP export helper classes.
    """

    def __init__(self, destination='', test=False):
        """
        Set common variables.
        """
        self.destination = destination
        self.test = test # boolean indicating whether to export all data or the first `self.test_entries`.
        self.test_entries = 100 # number of entries to process when --test=True
        self.examples = 5 # number of entries to write to the example files
        self.filenames = {} # defined in each class
        self.filehandles = {} # holds all open filehandles
        self.subfolders = { # names of subfolders
            'coordinates': 'genome_coordinates',
            'md5': 'md5',
            'sequences': 'sequences',
            'trackhub': os.path.join('genome_coordinates', 'track_hub'),
            'xrefs': 'id_mapping',
            'gpi': 'gpi',
        }
        logging.basicConfig(level='INFO')
        self.logger = logging.getLogger(self.__class__.__name__)

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
        """
        for filename, filepath in self.filenames.iteritems():
            self.filehandles[filename].close()
            if 'example' not in filename and 'readme' not in filename:
                self.gzip_file(filepath)
                os.remove(filepath)

    def gzip_file(self, filename):
        """
        Compress a given file using gzip, return the compressed file name.
        """
        gzipped_filename = '%s.gz' % filename
        cmd = 'gzip < %s > %s' % (filename, gzipped_filename)
        self.logger.info('Compressing file %s' % filename)
        status = subprocess.call(cmd, shell=True)
        if status == 0:
            self.logger.info('File compressed, new file %s' % gzipped_filename)
            return gzipped_filename
        else:
            self.logger.info('Compressing failed, no file created')
            return ''

    def log_database_error(self, pg_exception):
        """
        Log Postgres error message.
        """
        self.logger.critical('Postgres: %s' % pg_exception.message)

    ##################
    # Data retrieval #
    ##################

    def get_xrefs_with_genomic_coordinates(self, taxid):
        """
        Get RNA sequences with genomic coordinates.
        """
        xrefs = Xref.objects.select_related('accession__coordinates').\
                             filter(db__project_id__isnull=True).\
                             filter(taxid=taxid).\
                             filter(deleted='N').\
                             filter(accession__coordinates__chromosome__isnull=False).\
                             values_list('accession', flat=True).\
                             distinct()
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

    def create_genomic_readme(self):
        """
        ===================================================================
        RNAcentral Genomic Coordinates Data
        ===================================================================

        This directory contains genomic coordinates for a subset of RNAcentral ids
        where such mapping is available.

        * Bed
        Format description:
        http://www.ensembl.org/info/website/upload/bed.html
        http://genome.ucsc.edu/FAQ/FAQformat.html

        * Gff2
        Format description:
        http://www.sanger.ac.uk/resources/software/gff/spec.html

        * Gff3
        Format description:
        http://www.sequenceontology.org/gff3.shtml

        * track_hub/
        UCSC-style track hub description:
        https://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html

        Track hub folder structure:
        - genomes.txt [list of annotated genomes]
        - hub.txt [track hub description]
        - hg38 [human GRCh38 assembly]
        -- rnacentral.BigBed [bigBed binary data file]
        -- rnacentral.html []
        -- trackDb.txt [track description]
        """
        text = self.create_genomic_readme.__doc__
        text = self.format_docstring(text)
        f = open(self.get_output_filename('readme.txt', parent_dir=self.subdirectory), 'w')
        f.write(text)
        f.close()

    def create_release_notes_file(self):
        """
        ===================================================================
        RNAcentral Release {release_date}
        ===================================================================

        RNAcentral is an online resource for organising data
        about non-protein coding RNA genes.

        This release consists of {sequence_count} unique RNA sequences
        with {xrefs_count} cross-references to {database_count} Expert Databases.

        The release data are stored in subdirectories in this folder. Large data files
        are compressed with Gzip. Small uncompressed example files are also provided.
        Each folder contains a readme file with data description.

        RNAcentral is available online at http://rnacentral.org.
        For more ways of downloading the data go to http://rnacentral.org/downloads.
        """
        filename = self.get_output_filename('release_notes_template.txt')
        if os.path.exists(filename):
            self.logger.info('Release notes file already exists')
            return

        text = self.create_release_notes_file.__doc__
        text = self.format_docstring(text)

        release_date = time.strftime("%d/%m/%Y")
        sequence_count = intcomma(Rna.objects.count())
        xrefs_count = intcomma(Xref.objects.filter(deleted='N').count())
        database_count = intcomma(Database.objects.count())

        text = text.format(release_date=release_date,
                           sequence_count=sequence_count,
                           database_count=database_count,
                           xrefs_count=xrefs_count)
        f = open(filename, 'w')
        f.write(text)
        f.close()
