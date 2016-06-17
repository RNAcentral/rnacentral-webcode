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


# Redis results expiration time
EXPIRATION = 60*60*24*7 # seconds

# maximum time to run the job
MAX_RUN_TIME = 60*60*2 # seconds

# maximum number of entries that can be paginated over in EBI search
MAX_OUTPUT = 250000

# path to esl-sfetch binary, part of Infernal package
ESLSFETCH = os.path.join(os.environ.get('RNACENTRAL_LOCAL', ''), 'infernal-1.1.1', 'bin', 'esl-sfetch')

# path to fasta database
FASTA_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples.fasta')

# path to export search results
EXPORT_RESULTS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results')

# override default parameters using local_settings.py
try:
    from local_settings import *
except ImportError, e:
    pass

# create destination for the search results files
if not os.path.exists(EXPORT_RESULTS_DIR):
    os.makedirs(EXPORT_RESULTS_DIR)
