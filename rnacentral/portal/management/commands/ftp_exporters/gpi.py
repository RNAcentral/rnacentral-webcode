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
import subprocess

from collections import defaultdict

from portal.management.commands.ftp_exporters.ftp_base import FtpBase
from portal.management.commands.common_exporters.database_connection import cursor
from portal.utils import so_terms

"""
Export RNAcentral species-specific ids in GPI format.
The data are used for validation purposes in Protein2GO.

Usage:
python manage.py ftp_export -f gpi -d /path/to/destination

To run in test mode:
python manage.py ftp_export -f gpi -d /path/to/destination --test

GPI format documentation:
http://geneontology.org/page/gene-product-information-gpi-format

Example GPI file:
ftp://ftp.ebi.ac.uk/pub/databases/intact/current/various/intact_complex.gpi
"""


class GpiExporter(FtpBase):
    """
    Export RNAcentral species-specific ids in GPI format.
    """
    def __init__(self, *args, **kwargs):
        """
        Setup file path and store command line options.
        """
        super(GpiExporter, self).__init__(*args, **kwargs)
        self.subdirectory = self.make_subdirectory(self.destination,
                                                   self.subfolders['gpi'])
        self.filepath = os.path.join(self.subdirectory, 'rnacentral.gpi')
        self.precursor_rna = defaultdict(list)

    def export(self):
        """
        Main export function.
        """
        self.logger.info('Exporting gpi file %s' % self.filepath)
        self.get_mirna_precursors()
        self.write_gpi_file()
        self.clean_up()
        self.logger.info('GPI export complete')

    def write_gpi_file(self):
        """
        Write GPI file.
        """
        sql = """
        SELECT upi, taxid, description, rna_type
        FROM rnc_rna_precomputed
        WHERE taxid IS NOT NULL
        {test}
        """
        if self.test:
            test = "AND rna_type='miRNA'"
        else:
            test = ''
        with cursor() as cur:
            cur.execute(sql.format(test=test))
            with open(self.filepath, 'w') as filehandle:
                filehandle.write('!gpi-version: 1.2\n')
                for counter, result in enumerate(cur):
                    line = self.format_gpi_line(result)
                    filehandle.write(line)
                    if counter > self.test_entries:
                        break
        assert os.path.exists(self.filepath)
        self.test_unique_ids(self.filepath)
        self.test_none_taxids(self.filepath)
        self.gzip_file(self.filepath)

    def get_mirna_precursor_line(self, upi_taxid):
        """
        Format precursor_rna line.
        """
        if upi_taxid in self.precursor_rna:
            return 'precursor_rna=' + ','.join(set(self.precursor_rna[upi_taxid]))
        else:
            return ''

    def format_gpi_line(self, result):
        """
        Export a result row as a string in GPI format.
        """
        upi_taxid = '{upi}_{taxid}'.format(upi=result['upi'], taxid=result['taxid'])
        # the order of array elements defines the field order in the output
        keys = ['database', 'DB_Object_ID', 'DB_Object_Symbol',
                'DB_Object_Name', 'DB_Object_Synonym', 'DB_Object_Type',
                'Taxon', 'Parent_Object_ID', 'DB_Xref',
                'Gene_Product_Properties']
        data = dict()
        for key in keys:
            data[key] = ''
        data['database'] = 'RNAcentral'
        data['DB_Object_Name'] = result['description']
        data['DB_Object_ID'] = upi_taxid
        data['Taxon'] = 'taxon:{taxon}'.format(taxon=result['taxid'])
        data['DB_Object_Type'] = so_terms.get_label(result['rna_type'])
        data['Gene_Product_Properties'] = self.get_mirna_precursor_line(upi_taxid)
        # safeguard against breaking tsv format
        for key in keys:
            data[key] = data[key].replace('\t', ' ')
        return '\t'.join([data[key] for key in keys]) + '\n'

    def get_mirna_precursors(self):
        """
        Get miRNA precursors from miRBase for mature miRNAs.
        """
        sql = """
		SELECT
		    t1.upi as precursor, t4.upi as mature, t1.taxid
		FROM xref t1
		INNER JOIN rnc_accessions t2
		ON (t1.ac = t2.accession)
		INNER JOIN rnc_accessions t3
		ON (t2.external_id = t3.external_id)
		INNER JOIN xref t4
		ON (t3.accession = t4.ac)
		WHERE
            t1.dbid = 4
            AND t1.deleted = 'N'
            AND t2.accession != t3.accession
            AND t2.feature_name = 'precursor_RNA'
            AND t3.feature_name != 'precursor_RNA'
            AND t4.dbid = t1.dbid
            AND t1.upi != t4.upi
            AND t1.taxid = t4.taxid
        """
        self.logger.info('Looking for miRBase miRNA precursors')
        with cursor() as cur:
            cur.execute(sql)
            for result in cur:
                upi_taxid = '%s_%i' % (result['mature'], result['taxid'])
                self.precursor_rna[upi_taxid].append(result['precursor'])
        count = len(self.precursor_rna)
        self.logger.info('Found %i mature RNAs with precursors', count)

    @staticmethod
    def test_unique_ids(filename):
        """
        Test uniqueness of URS_taxid identifiers.
        """
        cmd = ['cat %s | wc -l' % filename]
        number_of_lines = subprocess.check_output(cmd, shell=True).strip()
        cmd = ["sort -u -t$'\t' -k2,2 %s | wc -l" % filename]
        number_of_unique_ids = subprocess.check_output(cmd, shell=True).strip()
        assert number_of_lines == number_of_unique_ids

    @staticmethod
    def test_none_taxids(filename):
        """
        Test that there are no None taxids.
        """
        cmd = ['grep _None %s | wc -l' % filename]
        none_taxids = subprocess.check_output(cmd, shell=True).strip()
        assert int(none_taxids) == 0
