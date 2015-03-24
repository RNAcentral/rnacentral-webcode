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
import shlex
import subprocess as sub

from local_settings import QUERY_DIR, RESULTS_DIR, NHMMER_EXECUTABLE, SEQDATABASE


class NhmmerError(Exception):
    """Raise when my specific value is wrong"""
    pass


class NhmmerSearch(object):
    """
    A class for launching nhmmer and storing results.
    """

    def __init__(self, sequence, job_id):
        """
        """
        self.sequence = sequence.replace('T', 'U').upper()
        self.job_id = job_id
        self.cmd = None
        self.params = {
            'query': None,
            'output': os.path.join(RESULTS_DIR, '%s.txt' % job_id),
            'nhmmer': NHMMER_EXECUTABLE,
            'db': SEQDATABASE,
            'incE': 0.01,
            'E': 0.01,
        }

    def create_query_file(self):
        """
        Write out query in fasta format.
        """
        self.params['query'] = os.path.join(QUERY_DIR, '%s.fasta' % self.job_id)
        with open(self.params['query'], 'w') as f:
            f.write('>query\n')
            f.write(self.sequence)
            f.write('\n')

    def get_command(self):
        """
        Get nhmmer command.
        """
        self.cmd = \
            ('{nhmmer} '
             '--qformat fasta '   # query format
             '--tformat hmmerfm ' # target format (precomputed binary db)
             '-o {output} '       # direct main output to a file
             '--incE {incE} '     # use an E-value of <= X as the inclusion threshold
             '-E {E} '            # report target sequences with an E-value of <= X
             '--rna '             # explicitly specify database alphabet
             '--toponly '         # search only top strand
             '{query} '           # query file
             '{db}').format(**self.params)

    def run_nhmmer(self):
        """
        Launch nhmmer.
        """
        if not self.cmd:
            self.get_command()
        process = sub.Popen(shlex.split(self.cmd), stdout=sub.PIPE,
                            stderr=sub.PIPE)
        output, errors = process.communicate()
        return_code = process.returncode
        if return_code != 0:
            raise NhmmerError(errors, output, return_code)

    def __call__(self):
        """
        Main entry point.
        """
        self.create_query_file()
        self.get_command()
        self.run_nhmmer()
        return self.params['output']
