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

from django.core.management.base import BaseCommand
from itertools import groupby
from subprocess import call
import re
import os


####################
# Import functions #
####################

def run():
    """
    """
    seq_db = '/Users/apetrov/Desktop/clustering/human.fasta'
    hmmer_exec = '/Users/apetrov/Desktop/clustering/hmmer-3.1b1-macosx-intel/src/nhmmer'
    query = '/Users/apetrov/Desktop/%s.fasta'
    temp_result = '/Users/apetrov/Desktop/result.txt'
    results_db = '/Users/apetrov/Desktop/results_database.txt'
    urs_regex = re.compile(r'URS[A-F0-9]{10}')

    def make_query_file(header, seq):
        """
        """
        fname = query % urs_regex.search(header).group()
        f = open(fname, 'w')
        f.write(header + "\n")
        f.write(seq)
        f.close()
        return fname

    def run_hmmer(query):
        """
        """
        cmd = '%s --tblout %s %s %s' % (hmmer_exec, temp_result, query, seq_db)
        print cmd
        call(cmd, shell=True)

    def append_results():
        """
        """
        cmd = 'cat %s >> %s' % (temp_result, results_db)
        call(cmd, shell=True)

    for header, seq in fasta_iter(seq_db):
        print header
        query_file = make_query_file(header, seq)
        run_hmmer(query_file)
        append_results()
        os.remove(query_file)


def fasta_iter(fasta_name):
    """
    given a fasta file. yield tuples of header, sequence
    """
    fh = open(fasta_name)
    # ditch the boolean (x[0]) and just keep the header or sequence since
    # we know they alternate.
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next().strip()#[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq



class Command(BaseCommand):
    """
    """

    ########################
    # Command line options #
    ########################

    # shown with -h, --help
    help = ('')

    def handle(self, *args, **options):
        """
        """
        run()
