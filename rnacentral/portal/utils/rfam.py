# -*- coding: utf-8 -*-

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

__doc__ = """
This module contains utility classes and functions for fetching and parsing
Rfam data from the FTP site.
"""

import re
import csv
import gzip
from cStringIO import StringIO
from ftplib import FTP

from functools32 import lru_cache

NON_ISNDC = set([
    'CRISPR',
    'antitoxin',
])

INFORMATIVE_NAMES = {
    'srp': 'SRP_RNA',
    'y_rna': 'Y_RNA',
    'hammerhead': 'hammerhead_ribozyme',
    'group-ii': 'autocatalytically_spliced_intron',
    'vault': 'vault_RNA',
    'tmrna': 'tmRNA',
}


def fetch_file(version, filename):
    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()
    ftp.cwd('pub/databases/Rfam/{version}'.format(
        version=version,
    ))
    command = 'RETR {filename}'.format(filename=filename)
    raw = StringIO()
    ftp.retrbinary(command, raw.write)
    ftp.quit()
    raw.seek(0)
    if filename.endswith('.gz'):
        raw = gzip.GzipFile(fileobj=raw, mode='rb')
    return raw


def get_isndc(raw):
    if not raw:
        return None
    processed = raw.rstrip(';').split('; ')
    if not processed:
        return None
    if not filter(None, processed):
        return None
    if len(processed) == 1:
        return None
    if processed[0] == 'Cis-reg':
        if processed[1] == 'riboswitch':
            return 'riboswitch'
        return None
    if len(processed) == 2:
        if processed[-1] == 'sRNA':
            return 'ncRNA'
        if processed[-1] == 'miRNA':
            return 'precursor_RNA'
        if processed[-1] in NON_ISNDC:
            return None
        return processed[-1]
    if 'snoRNA' in processed:
        return 'snoRNA'
    return None


def get_families(version='CURRENT'):
    raw = fetch_file(version=version, filename='database_files/family.txt.gz')
    return list(csv.reader(raw, delimiter='\t'))


def get_clans(version='CURRENT'):
    raw = fetch_file(version=version, filename='database_files/clan.txt.gz')
    return list(csv.reader(raw, delimiter='\t'))


def get_clan_membership(version='CURRENT'):
    raw = fetch_file(version=version, filename='database_files/clan_membership.txt.gz')
    return list(csv.reader(raw, delimiter='\t'))


@lru_cache()
def name_to_isnsdc_type(version='CURRENT'):
    mapping = {}
    families = get_families(version=version)
    for row in families:
        if not row:
            continue

        name = row[1]
        insdc = get_isndc(row[18])
        for pattern, rna_type in INFORMATIVE_NAMES.items():
            if re.search(pattern, name, re.IGNORECASE):
                insdc = rna_type
        mapping[name] = insdc
    return mapping
