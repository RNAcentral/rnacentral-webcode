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

import os
import shlex
import subprocess as sub

from settings import QUERY_DIR, RESULTS_DIR, NHMMER_EXECUTABLE, SEQDATABASE


class NhmmerSearch(object):
    """
    Class for launching nhmmer and storing results.
    """
    def __init__(self, sequence, job_id):
        """
        Initialize internal variables.
        """
        self.sequence = sequence.replace('T', 'U').upper()
        self.job_id = job_id
        self.cmd = None
        self.params = {
            'query': os.path.join(QUERY_DIR, '%s.fasta' % job_id),
            'output': os.path.join(RESULTS_DIR, '%s.txt' % job_id),
            'nhmmer': NHMMER_EXECUTABLE,
            'db': SEQDATABASE,
            'cpu': 4,
        }
        self.set_e_values()

    def set_e_values(self):
        """
        Set E-values dynamically depending on the query sequence length.
        The values were computed by searching the full dataset
        using random short sequences as queries
        with an extremely high E-value and recording
        the E-values of the best hit.
        """
        length = len(self.sequence)
        if length <= 30:
            e_value = pow(10, 5)
        elif length > 30 and length <= 40:
            e_value = pow(10, 2)
        elif length > 40 and length <= 50:
            e_value = pow(10, -1)
        else:
            e_value = pow(10, -2)
        self.params['incE'] = e_value
        self.params['E'] = e_value

    def create_query_file(self):
        """
        Write out query in fasta format.
        """
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
             '--tformat fasta '   # target format
             '-o {output} '       # direct main output to a file
             '--incE {incE} '     # use an E-value of <= X as the inclusion threshold
             '-E {E} '            # report target sequences with an E-value of <= X
             '--rna '             # explicitly specify database alphabet
             '--toponly '         # search only top strand
             '--cpu {cpu} '       # number of CPUs to use
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
            class NhmmerError(Exception):
                """Raise when nhmmer exits with a non-zero status"""
                pass
            raise NhmmerError(errors, output, return_code)

    def __call__(self):
        """
        Main entry point.
        """
        self.create_query_file()
        self.get_command()
        self.run_nhmmer()
        return self.params['output']
