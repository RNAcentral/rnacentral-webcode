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

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
import logging
import os
import shutil
import time


class TrackhubExporter(FtpBase):
    """
    Create UCSC track hub output files.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super(TrackhubExporter, self).__init__(*args, **kwargs)

        self.subdirectory = self.make_subdirectory(self.destination, self.subfolders['trackhub'])
        self.logger = logging.getLogger(__name__)

    def export(self, all_genomes={}):
        """
        Main export function.
        """
        def get_bigbed_name():
            """
            Get the name of the bigBed file for a genome.
            """
            parent_dir = os.path.join(self.destination, self.subfolders['coordinates'])
            return self.get_output_filename('%s.bigBed' % genome['assembly_ucsc'], parent_dir=parent_dir)

        self.logger.info('Exporting track hub to %s' % self.subdirectory)

        hub = Hub(subdirectory=self.subdirectory)
        hub.render()

        genomes = Genomes(subdirectory=self.subdirectory, genomes=all_genomes)
        genomes.render()

        for genome in all_genomes:
            if not genome['assembly_ucsc']:
                continue
            bigBed = get_bigbed_name()
            trackDb = TrackDb(subdirectory=self.subdirectory, genome=genome['assembly_ucsc'], html="", bigBed=bigBed) # can customize html if necessary
            trackDb.render()

        self.logger.info('Track hub export complete')


class HubBase(object):
    """
    Base class for all other track hub classes.

    Example Track Hub structure:

    track_hub/
        hub.txt
        genomes.txt
        hg18/
            rnacentral.bigBed
            rnacentral.html
            trackDb.txt
        hg19/
            rnacentral.bigBed
            rnacentral.html
            trackDb.txt
    """

    def __init__(self, subdirectory=''):
        """
        """
        self.subdirectory = subdirectory
        self.logger = logging.getLogger(__name__)

    def get_hub_path(self, filename):
        """
        Get full path to the corresponding file on disk.
        """
        return os.path.join(self.subdirectory, filename)

    def _render(self, data):
        """
        Render an array of dictionaries as a file on disk.
        """
        self.logger.info('Writing file %s' % self.filename)
        filename = self.get_hub_path(self.filename)
        f = open(filename, 'w')
        for entry in data:
            for key, value in sorted(entry.items()):
                line = '{0} {1}\n'.format(key, value)
                f.write(line)
            f.write('\n')
        f.close()
        self.logger.info('File created')


class Genomes(HubBase):
    """
    File genomes.txt

    Example:
    genome hg18
    trackDb hg18/trackDb.txt

    genome hg19
    trackDb hg19/trackDb.txt
    """

    def __init__(self, subdirectory='', genomes=[]):
        """
        """
        super(Genomes, self).__init__(subdirectory=subdirectory)
        self.filename = 'genomes.txt'
        self.genomes = genomes

    def render(self):
        """
        """
        data = []
        for genome in self.genomes:
            if not genome['assembly_ucsc']:
                continue
            data.append({
                'genome' : genome['assembly_ucsc'],
                'trackDb': os.path.join(genome['assembly_ucsc'], 'trackDb.txt'),
            })
        self._render(data)


class Hub(HubBase):
    """
    Create file hub.txt
    """

    def __init__(self, subdirectory=''):
        """
        """
        super(Hub, self).__init__(subdirectory=subdirectory)
        self.filename = 'hub.txt'

    def render(self):
        """
        Write the file to the disk.
        """
        data = [{
            'hub'        : 'rnacentral',
            'shortLabel' : 'RNAcentral Hub',
            'longLabel'  : 'Unique RNAcentral sequences',
            'genomesFile': 'genomes.txt',
            'email'      : 'helpdesk@rnacentral.org',
        }]
        self._render(data)


class TrackDb(HubBase):
    """
    Genome-specific trackDb files.
    """

    def __init__(self, subdirectory='', genome='', html='', bigBed=''):
        """
        Set internal variables.
        """
        super(TrackDb, self).__init__(subdirectory=subdirectory)
        self.genome = genome
        self.html = html
        self.bigBed = bigBed
        self.base_url = 'http://rnacentral.org'

    def get_track_db_path(self, filename):
        """
        Get the path for a genome within the hub.
        Example:
        hub/
            hub.txt
            hg18/ <- this path
            hg19/
        """
        track_path = self.get_hub_path(self.genome)
        if not os.path.exists(track_path):
            os.mkdir(track_path)
        return os.path.join(track_path, filename)

    def render(self):
        """
        Create a folder with all files for the given genome.
        """
        self.render_html()
        self.render_track_db_file()
        self.move_bigBed_file()

    def move_bigBed_file(self):
        """
        Move the bigBed file from the `genome_coordinates` subdirectory
        to the `track_hub` subdirectory.
        """
        src = self.bigBed
        dst = self.get_track_db_path('rnacentral.bigBed')
        if os.path.exists(src):
            shutil.move(src, dst)
            self.logger.info('File %s moved to %s' % (src, dst))
        else:
            self.logger.error('bigBed %s not found' % src)

    def render_html(self):
        """
        The html page shown when an entry is clicked in UCSC browser.
        """
        html = """
        <h1>RNAcentral Hub</h1>

        <p>
        Each unique RNAcentral entry groups together all identical RNA sequences no matter what species they are from
        and assigns a stable id.
        </p>

        {0}

        <p>
        Find out more at <a href="{1}" target="_blank">{1}</a>
        </p>
        """.format(self.html, self.base_url)

        filename = self.get_track_db_path('rnacentral.html')
        f = open(filename, 'w')
        f.write(html)
        f.close()

    def render_track_db_file(self):
        """
        Create file trackDb.txt
        """
        dataVersion = time.strftime("%d/%m/%Y")

        self.filename = self.get_track_db_path('trackDb.txt')
        trackDb = {
            'track'       : 'rnacentral',
            'bigDataUrl'  : 'rnacentral.bigBed',
            'shortLabel'  : 'RNAcentral',
            'longLabel'   : 'Unique RNAcentral sequences',
            'bedNameLabel': 'Unique RNAcentral sequences',
            'type'        : 'bigBed 12', # 12-column bigBed file
            'itemRgb'     : 'on', # use colours from the bigBed file
            'exonArrows'  : 'on',
            'visibility'  : 'full',
            'url'         : '{0}/rna/$$'.format(self.base_url), # url for the RNAcentral entry
            'urlLabel'    : 'View in RNAcentral:',
            'dataVersion' : dataVersion,
        }
        self._render([trackDb])
