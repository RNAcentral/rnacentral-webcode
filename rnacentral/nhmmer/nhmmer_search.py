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

from nhmmer.local_settings import QUERY_DIR, RESULTS_DIR, NHMMER_EXECUTABLE, SEQDATABASE
from nhmmer.models import Query, Results
from nhmmer.nhmmer_parse import NhmmerResultsParser


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
        self.sequence = sequence.replace('T','U').upper()
        self.job_id = job_id
        self.cmd = None
        self.params = {
            'query': None,
            'out': os.path.join(RESULTS_DIR, '%s.txt' % job_id),
            'alignments': os.path.join(RESULTS_DIR, '%s_alignments.txt' % job_id),
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
             '--tblout {out} '    # store tabular output in a file
             '-o {alignments} '   # discard main output
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
        p = sub.Popen(shlex.split(self.cmd), stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        return_code = p.returncode
        if return_code != 0:
            raise NhmmerError(errors, output, return_code)
        return return_code

    def parse_results(self):
        """
        Parse results text files
        and save the data in the database.
        """
        results = []
        for record in NhmmerResultsParser(filename=self.params['alignments'])():
            results.append(Results(query_id=self.job_id,
                                   result_id=record['result_id'],
                                   rnacentral_id=record['rnacentral_id'],
                                   description=record['description'],
                                   score=record['score'],
                                   bias=record['bias'],
                                   e_value=record['e_value'],
                                   query_start=record['query_start'],
                                   query_end=record['query_end'],
                                   target_length=record['target_length'],
                                   target_start=record['target_start'],
                                   target_end=record['target_end'],
                                   alignment=record['alignment']))
        Results.objects.bulk_create(results)

        query = Query(id=self.job_id, query=self.sequence, length=len(self.sequence))
        query.save()

    def __call__(self):
        """
        Main entry point.
        """
        self.create_query_file()
        self.get_command()
        status = self.run_nhmmer()
        self.parse_results()
        return status
