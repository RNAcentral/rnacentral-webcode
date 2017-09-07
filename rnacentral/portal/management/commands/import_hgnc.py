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

import json
import requests
from datetime import datetime

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from portal.models import Xref, Accession, Database, Release, Reference
from portal.models.reference_map import Reference_map

"""
Import HGNC xrefs into RNAcentral.

Usage:
python manage.py import_hgnc -i /path/to/hgnc/json/file

To run in test mode:
python manage.py import_hgnc -i /path/to/hgnc/json/file -t
"""

class HGNCImporter():
    """
    Class for importing HGNC xrefs into RNAcentral.
    """
    def __init__(self, **kwargs):
        """
        Store command line options and get a mapping between HGNC ncRNA locus
        types and INSDC ncRNA vocabulary.
        """
        self.test = kwargs['test']
        self.hgnc_json_file = kwargs['json_file']
        self.data = None
        self.database = Database.objects.get(descr='HGNC')
        self.release = Release.objects.get(db_id=self.database.id)
        self.hgnc = {
            'RNA, Y': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'Y_RNA',
            },
            'RNA, cluster': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'other',
            },
            'RNA, long non-coding': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'lncRNA',
            },
            'RNA, micro': {
                'feature_name': 'precursor_RNA',
                'ncrna_type': '',
            },
            'RNA, misc': {
                'feature_name': 'misc_RNA',
                'ncrna_type': '',
            },
            'RNA, ribosomal': {
                'feature_name': 'rRNA',
                'ncrna_type': '',
            },
            'RNA, small cytoplasmic': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'scRNA',
            },
            'RNA, small nuclear': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'snRNA',
            },
            'RNA, small nucleolar': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'snoRNA',
            },
            'RNA, transfer': {
                'feature_name': 'tRNA',
                'ncrna_type': '',
            },
            'RNA, vault': {
                'feature_name': 'ncRNA',
                'ncrna_type': 'vault_RNA',
            },
        }

    def get_hgnc_data(self):
        """
        Read input data from a JSON file.
        """
        with open(self.hgnc_json_file, 'r') as f:
            self.data = json.load(f)

    def delete_existing_hgnc_data(self):
        """
        Delete all already imported HGNC data so that there are no stale
        cross-references.
        """
        print 'Deleting existing HGNC Xrefs, Accessions, and Reference_maps'
        Xref.objects.filter(db_id=self.database.id).delete()
        Reference_map.objects.filter(accession__database=self.database.descr).delete()
        Accession.objects.filter(database=self.database.descr).delete()

    def import_data(self):
        """
        Import data into the database.
        """
        hgnc_main_pmid = self.database.references()[0]['pubmed_id']
        hgnc_ref_id = self.get_publication_info(hgnc_main_pmid)

        count = 0
        for i, entry in enumerate(self.data):
            if self.test and i > 20:
                break
            if not entry['rnacentral_id']:
                # some entries may not have been mapped to RNAcentral.
                continue
            print entry['symbol']
            Xref.objects.update_or_create(
                db_id=self.database.id,
                accession_id=entry['hgnc_id'],
                created_id=self.release.id,
                last_id=self.release.id,
                upi_id=entry['rnacentral_id'],
                version_i=1,
                deleted='N',
                timestamp=datetime.now(),
                userstamp='RNACEN',
                version=1,
                taxid=9606
            )
            Accession.objects.update_or_create(
                accession=entry['hgnc_id'],
                description='Homo sapiens ' + entry['name'],
                division='HUM',
                species='Homo sapiens',
                is_composite='N',
                database='HGNC',
                classification='Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini; Catarrhini; Hominidae; Homo; Homo sapiens',
                external_id=entry['symbol'],
                feature_name=self.get_feature_name(entry['locus_type']),
                ncrna_class=self.get_ncrna_class(entry['locus_type']),
                gene=entry['symbol'],
                gene_synonym=';'.join(entry['prev_symbol']) if 'prev_symbol' in entry else '',
                note=json.dumps(entry)
            )

            Reference_map.objects.update_or_create(
                accession_id=entry['hgnc_id'],
                data_id=hgnc_ref_id
            )
            if 'pubmed_id' in entry:
                for pubmed_id in entry['pubmed_id']:
                    ref = self.get_publication_info(pubmed_id)
                    if ref:
                        Reference_map.objects.update_or_create(
                            accession_id=entry['hgnc_id'],
                            data_id=ref
                        )
            count += 1
        print '%i entries imported' % count

    def get_publication_info(self, pmid):
        """
        Check in the database if the reference is already there.
        In case of duplicate references, pick the one with lowest id to ensure
        reproducibility.

        """
        refs = Reference.objects.filter(pubmed=pmid).order_by('id').all()
        if refs:
            return refs[0].id
        else:
            return None

        # url = 'http://www.ebi.ac.uk/europepmc/webservices/rest/search?query=ext_id:{pmid}%20src:med&format=json'.format(pmid=pmid)
        # data = requests.get(url).json()
        # if not data['resultList']['result']:
        #     return None

    def get_feature_name(self, locus_type):
        """
        Access feature name for HGNC ncRNA locus.
        """
        return self.hgnc[locus_type]['feature_name']

    def get_ncrna_class(self, locus_type):
        """
        Access ncrna_class for HGNC ncRNA locus.
        """
        return self.hgnc[locus_type]['ncrna_type']

    def __call__(self):
        """
        Main import function.
        """
        print 'Importing data from HGNC'
        self.get_hgnc_data()
        self.delete_existing_hgnc_data()
        self.import_data()
        print 'Done'


class Command(BaseCommand):
    """
    Handle command line options.
    """
    option_list = BaseCommand.option_list + (
        make_option('-i', '--input',
            dest='json_file',
            default=False,
            help='[Required] Path to HGNC JSON file with RNAcentral identifiers'),
        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='[Optional] Run in test mode, which does not change the data in the database.'),
    )
    # shown with -h, --help
    help = ('Import HGNC cross-references into RNAcentral database')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        if not options['json_file']:
            raise CommandError('Please specify HGNC input file')
        HGNCImporter(**options)()
