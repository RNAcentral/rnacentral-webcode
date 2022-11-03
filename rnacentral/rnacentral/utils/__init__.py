"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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
import re


def get_environment():
    """
    Detect host environment: HX, HH or DEV.
    """
    hostname = os.environ.get("HTTP_PROXY")
    if hostname:
        match = re.search(r"http://(\w+)-\w+\.ebi\.ac\.uk", hostname)
        if match and match.group(1) in ["hx", "hh"]:
            env = match.group(1)
        else:
            env = "dev"
    else:
        env = "dev"
    return env.upper()
