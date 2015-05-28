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
    Class for parsing nhmmer search results.
    """
    def __init__(self, filename=''):
        """
        """
        self.filename = filename
        self.stats_text = 'Internal pipeline statistics summary'
        self.query_length = 0

    def record_generator(self, f, delimiter='\n', bufsize=4096):
        """
        Read file using input record separator.
        Based on this SO question:
        http://stackoverflow.com/questions/19600475/how-to-read-records-terminated-by-custom-separator-from-file-in-python
        """
        buf = ''
        while True:
            newbuf = f.read(bufsize)
            if not newbuf:
                yield buf
                return
            buf += newbuf
            lines = buf.split(delimiter)
            for line in lines[:-1]:
                yield line
            buf = lines[-1]

    def parse_record_description(self, lines):
        """
        Example:
 URS0000000013  Vibrio gigantis partial 16S ribosomal RNA
    score  bias    Evalue   hmmfrom    hmm to     alifrom    ali to      envfrom    env to       sq len      acc
   ------ ----- ---------   -------   -------    --------- ---------    --------- ---------    ---------    ----
 !   76.9   4.1   5.4e-23        67       196 ..        41       170 ..        21       175 ..      1421    0.94
        """
        def parse_first_line(line):
            """
            Get URS id and description.
            """
            match = re.search(r'URS[0-9A-Fa-f]{10}', line)
            return {
                'rnacentral_id': match.group(),
                'description': line.replace(match.group(), '').replace(';', '').strip(),
            }

        def parse_fourth_line(line):
            """
            Parse out hit statistics.
            """
            line = line.replace('!', '').\
                        replace('?', '').\
                        replace('[]', '').\
                        replace('[.', '').\
                        replace('.]', '').\
                        replace('..', '').\
                        strip()
            scores = re.split(r' +', line)
            return {
                'score': float(scores[0]),
                'bias': float(scores[1]),
                'e_value': float(scores[2]),
                'target_length': int(scores[9]),
            }

        data = parse_first_line(lines[0])
        data.update(parse_fourth_line(lines[3]))
        return data

    def parse_alignment(self, lines, target_length):
        """
        Example:
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
        alignment = []
        alignment_length = 0
        matches = 0
        nts_count1 = 0
        nts_count2 = 0
        gap_count = 0

        for i, line in enumerate(lines):
            gaps = line.count('-') + line.count('.')
            if i % 5 == 0: # query
                match = re.match(r'^(\s+query\s+\d+ )(.+) \d+', line)
                if match:
                    label = match.group(1)
                    block_length = len(match.group(2))
                    alignment_length += block_length
                    line = line.upper().replace('.', '-').replace('QUERY', 'Query')
                    line = re.sub('^\s+', '', line)
                    alignment.append(line)
                    match2 = re.match('^Query\s+\d+ ', line)
                    whitespace = len(match2.group(0))
                    nts_count1 += block_length - gaps
                    gap_count += gaps
            elif i % 5 == 1: # matches
                line = ' ' * whitespace + re.sub('\w', '|', line[len(label):])
                matches += line.count('|')
                alignment.append(line)
            elif i % 5 == 2: # target
                line = re.sub('\s+URS[0-9A-Fa-f]{10};?', 'Sbjct', line.upper())
                match = re.match(r'^Sbjct\s+\d+ (.+) \d+', line)
                if match:
                    block_length = len(match.group(1))
                    nts_count2 += block_length - gaps
                    gap_count += gaps
                alignment.append(line)
            elif i % 5 == 3: # skip nhmmer confidence lines
                pass
            elif i % 5 == 4: # blank line
                alignment.append(line)

        return {
            'alignment': '\n'.join(alignment).strip(),
            'alignment_length': alignment_length,
            'gap_count': gap_count,
            'match_count': matches,
            'nts_count1': nts_count1,
            'nts_count2': nts_count2,
            'identity': (float(matches) / alignment_length) * 100,
            'query_coverage': (float(nts_count1) / self.query_length) * 100,
            'target_coverage': (float(nts_count2) / target_length) * 100,
            'gaps': (float(gap_count) / alignment_length) * 100,
        }

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
        data = self.parse_record_description(lines[:6])
        data.update(self.parse_alignment(lines[7:], data['target_length']))
        data['query_length'] = self.query_length
        return data

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

    def get_query_length(self, record):
        """
        Get query sequence length.
        Example line:
        Query:       query  [M=2905]
        """
        match = re.search(r'Query:       query  \[M=(\d+)\]', record)
        if match:
            self.query_length = int(match.group(1))

    def __call__(self):
        """
        Split file into matches and return parsed data.
        """
        with open(self.filename, 'r') as f:
            for i, record in enumerate(self.record_generator(f, '>>')):
                if i == 0:
                    # first block with job stats
                    self.get_query_length(record)
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
    import sys
    if len(sys.argv) < 2:
        print 'Provide full path to the input file with nhmmer search results'
        sys.exit(1)
    filename = sys.argv[1]
    for record in NhmmerResultsParser(filename=filename)():
        print record
