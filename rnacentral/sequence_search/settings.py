"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
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

# SEQUENCE_SEARCH_ENDPOINT = 'http://193.62.55.45' # running remotely with a proxy
SEQUENCE_SEARCH_ENDPOINT = 'http://193.62.55.123:8002' # running remotely without a proxy
# SEQUENCE_SEARCH_ENDPOINT = 'http://193.62.55.44:8002' # running remotely without a proxy
# SEQUENCE_SEARCH_ENDPOINT = 'http://host.docker.internal:8002' # running locally
# SEQUENCE_SEARCH_ENDPOINT = 'https://search.rnacentral.org'

# minimum query sequence length
MIN_LENGTH = 10

# maximum query sequence length
MAX_LENGTH = 7000
