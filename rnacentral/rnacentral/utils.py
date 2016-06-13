"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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

import re
import socket


def get_environment():
    """
    Detect host environment: HX, OY, PG or DEV.
    """
    hostname = socket.gethostname()
    match = re.search(r'ves-(\w+)-\w+\.ebi\.ac\.uk', hostname)
    if match and match.group(1) in ['hx', 'pg', 'oy']:
        env = match.group(1)
    else:
        env = 'dev'
    return env.upper()
