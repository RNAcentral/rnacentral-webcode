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

# minimum query sequence length
MIN_LENGTH = 11

# maximum query sequence length
MAX_LENGTH = 10000

# Redis results expiration time
EXPIRATION = 60*60*24*7 # seconds

# maximum time to run nhmmer
MAX_RUN_TIME = 60*60 # seconds

# full path to query files
QUERY_DIR = ''

# full path to results files
RESULTS_DIR = ''

# full path to nhmmer executable
NHMMER_EXECUTABLE = ''

# full path to sequence database
SEQDATABASE = ''
