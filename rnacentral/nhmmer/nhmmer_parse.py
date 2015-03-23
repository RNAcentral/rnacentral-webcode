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

import re


class NhmmerResultsParser(object):
    """
    A class for parsing nhmmer search results.
    """
    def __init__(self, filename=''):
        """
        """
        self.filename = filename
        self.stats_text = 'Internal pipeline statistics summary'

    def record_generator(self, file, delimiter='\n', bufsize=4096):
        """
        Read file using input record separator.
        Based on this SO question:
        http://stackoverflow.com/questions/19600475/how-to-read-records-terminated-by-custom-separator-from-file-in-python
        """
        buf = ''
        while True:
            newbuf = file.read(bufsize)
            if not newbuf:
                yield buf
                return
            buf += newbuf
            lines = buf.split(delimiter)
            for line in lines[:-1]:
                yield line
            buf = lines[-1]

    def parse_record(self, text):
        """
        Example record:
 URS0000000013  Vibrio gigantis partial 16S ribosomal RNA
    score  bias    Evalue   hmmfrom    hmm to     alifrom    ali to      envfrom    env to       sq len      acc
   ------ ----- ---------   -------   -------    --------- ---------    --------- ---------    ---------    ----
 !   76.9   4.1   5.4e-23        67       196 ..        41       170 ..        21       175 ..      1421    0.94

  Alignment:
  score: 76.9 bits
          query  67 gagcggcggacgggugaguaaugccuaggaaucugccugguagugggggauaacgcucggaaacggacgcuaauaccgcauacguccuacgggaga 162
                    gagcggcggacgggugaguaaugccuaggaa  ugccu g  gugggggauaac  u ggaaacg   gcuaauaccgcaua   ccuacggg  a
  URS0000000013  41 GAGCGGCGGACGGGUGAGUAAUGCCUAGGAAAUUGCCUUGAUGUGGGGGAUAACCAUUGGAAACGAUGGCUAAUACCGCAUAAUGCCUACGGGCCA 136
                    789********************************************************************************************* PP

          query 163 aagcaggggaccuucgggccuugcgcuaucagau 196
                    aag  ggggaccuucgggccu  cgc    agau
  URS0000000013 137 AAGAGGGGGACCUUCGGGCCUCUCGCGUCAAGAU 170
                    *********************9999877777766 PP
        """
        lines = text.split('\n')

        line3 = lines[3].replace('!','').strip()
        scores = re.split(r'\s{2,}', line3)

        match = re.search(r'URS[0-9A-Fa-f]{10}', lines[0])
        rnacentral_id = match.group() if match else 'Unknown RNAcentral id'
        description = lines[0].replace(rnacentral_id,'').strip()

        return {
            'rnacentral_id': rnacentral_id,
            'description': description,
            'score': scores[0],
            'bias': scores[1],
            'e_value': scores[2],
            'query_start': scores[3].split(' ')[0],
            'query_end': scores[4].split(' ')[0],
            'target_start': scores[5].split(' ')[0],
            'target_end': scores[6].split(' ')[0],
            'target_length': int(scores[9]),
            'alignment': '\n'.join(lines[7:len(lines)-2]),
        }

    def is_last_record(self, record):
        """
        Last record contains internal query statistics.
        """
        if self.stats_text in record:
            return True
        else:
            return False

    def strip_out_internal_stats(self, record):
        """
        Delete lines with internal query statistics.
        """
        delete = 0
        lines = record.split('\n')
        for i, line in enumerate(lines):
            if self.stats_text in line:
                delete = i
                break
        if delete:
            lines = lines[:delete]
        return '\n'.join(lines)

    def __call__(self):
        """
        Split file into matches and return parsed data.
        """
        with open(self.filename, 'r') as f:
            for i, record in enumerate(self.record_generator(f, '>>')):
                if i == 0:
                    # skip first block with job stats
                    continue
                if self.is_last_record(record):
                    record = self.strip_out_internal_stats(record)
                data = self.parse_record(record)
                data['result_id'] = i
                yield data


if __name__ == "__main__":
    """
    Run from command line for testing purposes.
    """
    import os
    import sys
    if len(sys.argv) < 2:
        print 'Provide full path to the input file with nhmmer search results'
        sys.exit(1)
    filename = sys.argv[1]
    for record in NhmmerResultsParser(filename=filename)():
        print record
