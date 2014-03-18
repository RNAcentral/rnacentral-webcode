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

import os
import shutil
import time


class HubBase:
    """
    Base class for all other track hub classes.

    Track Hub structure:

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

    def get_hub_path(self, filename):
        """
        Get full path to the corresponding file on disk.
        """
        if not os.path.exists(self.destination):
            os.mkdir(self.destination)
        return os.path.join(self.destination, filename)

    def _render(self, data):
        """
        Render an array of dictionaries as a file on disk.
        """
        print 'Writing file %s' % self.filename
        filename = self.get_hub_path(self.filename)
        f = open(filename, 'w')
        for entry in data:
            for key, value in sorted(entry.items()):
                line = '{0} {1}\n'.format(key, value)
                f.write(line)
            f.write('\n')
        f.close()
        print 'File created'


class Genomes(HubBase):
    """
    File genomes.txt

    Example:
    genome hg18
    trackDb hg18/trackDb.txt

    genome hg19
    trackDb hg19/trackDb.txt
    """

    def __init__(self, destination='', genomes=[]):
        """
        """
        self.destination = destination
        self.filename = 'genomes.txt'
        self.genomes = genomes

    def render(self):
        """
        """
        data = []
        for genome in self.genomes:
            data.append({
            'genome' : genome,
            'trackDb': os.path.join(genome, 'trackDb.txt'),
        })
        self._render(data)


class Hub(HubBase):
    """
    Create file hub.txt
    """

    def __init__(self, destination=''):
        """
        """
        self.destination = destination
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

    def __init__(self, destination='', genome='', html='', bigBed=''):
        """
        Set internal variables.
        """
        self.destination = destination
        self.genome = genome
        self.html = html
        self.bigBed = bigBed
        self.base_url = 'http://test.rnacentral.org' # todo: determine dynamically

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
        self.copy_bigBed_file()

    def copy_bigBed_file(self):
        """
        """
        trackhub_bigBed = self.get_track_db_path('rnacentral.bigBed')
        if os.path.exists(self.bigBed):
            shutil.copyfile(self.bigBed, trackhub_bigBed)
        else:
            print 'Error: bigBed %s not found' % self.bigBed

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
