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

from django.db import models
from django.db.models import Min, Max
from django.utils.functional import cached_property
from django.template.defaultfilters import pluralize
import re

# to make text fields searchable, add character set functional indexes in Oracle
# CREATE INDEX index_name ON table_name(SYS_OP_C2C(column_name));


class Rna(models.Model):
    upi = models.CharField(max_length=13, db_index=True, primary_key=True)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    crc64 = models.CharField(max_length=16)
    length = models.IntegerField(db_column='len')
    seq_short = models.CharField(max_length=4000)
    seq_long = models.TextField()
    md5 = models.CharField(max_length=32, unique=True, db_index=True)

    class Meta:
        db_table = 'rna'

    def get_sequence(self):
        """
        Sequences of up to 4000 nucleotides are stored in seq_short, while the
        longer ones are in stored in seq_long as CLOB objects
        due to Oracle column size restrictions.
        """
        if self.seq_short:
            sequence = self.seq_short
        else:
            sequence = self.seq_long
        return sequence.replace('T', 'U').upper()

    def count_symbols(self):
        seq = self.get_sequence()
        count_A = seq.count('A')
        count_C = seq.count('C')
        count_G = seq.count('G')
        count_U = seq.count('U')
        return {
            'A': count_A,
            'U': count_U,
            'C': count_C,
            'G': count_G,
            'N': len(seq) - (count_A + count_C + count_G + count_U)
        }

    def get_expert_database_xrefs(self):
        """
        Get xrefs from expert databases.
        """
        return self.xrefs.select_related().exclude(accession__is_composite='N').all()

    def get_ena_xrefs(self):
        """
        Get ENA xrefs that don't have corresponding expert database entries.
        """
        expert_db_projects = Database.objects.exclude(project_id=None).\
                                              values_list('project_id', flat=True)
        return self.xrefs.filter(db__descr='ENA').\
                          exclude(accession__project__in=expert_db_projects).\
                          select_related().\
                          all()

    def get_refseq_xrefs(self):
        """
        Get RefSeq xrefs, which require separate treatment because they are not
        part of the Non-coding product.
        """
        return self.xrefs.filter(db__descr='REFSEQ').select_related().all()

    def get_rfam_xrefs(self):
        """
        Get RFAM xrefs, which require separate treatment because they are not
        part of the Non-coding product.
        """
        return self.xrefs.filter(db__descr='RFAM').select_related().all()

    def get_xrefs(self):
        """
        Concatenate querysets putting the expert database xrefs
        at the beginning of the resulting queryset.
        """
        return self.get_ena_xrefs() | self.get_rfam_xrefs() | self.get_refseq_xrefs() | self.get_expert_database_xrefs()

    def count_xrefs(self):
        """
        Count the number of cross-references associated with the sequence.
        """
        return self.xrefs.count()

    @cached_property
    def count_distinct_organisms(self):
        """
        Count the number of distinct taxids referenced by the sequence.
        """
        return self.xrefs.values('accession__species').distinct().count()

    @cached_property
    def count_distinct_databases(self):
        """
        Count the number of distinct databases referenced by the sequence.
        """
        return self.xrefs.values('db_id').distinct().count()

    @cached_property
    def first_seen(self):
        """
        Return the earliest release the sequence is referenced in.
        """
        data = self.xrefs.aggregate(first_seen=Min('created__release_date'))
        return data['first_seen']

    @cached_property
    def last_seen(self):
        """
        Like `first_seen` but with reversed order.
        """
        data = self.xrefs.aggregate(last_seen=Max('last__release_date'))
        return data['last_seen']

    def get_sequence_fasta(self):
        """
        Split long sequences by a fixed number of characters per line.
        """
        max_column = 80
        seq = self.get_sequence()
        split_seq = ''
        i = 0
        while i < len(seq):
            split_seq += seq[i:i+max_column] + "\n"
            i += max_column
        fasta = ">%s; %s\n%s" % (self.upi, self.get_description(), split_seq)
        return fasta

    def get_gff(self):
        """
        Format genomic coordinates from all xrefs into a single file in GFF2 format.
        """
        xrefs = self.xrefs.filter(db_id=1).all()
        gff = ''
        for xref in xrefs:
            gff += _xref_to_gff_format(xref)
        return gff

    def get_gff3(self):
        """
        Format genomic coordinates from all xrefs into a single file in GFF3 format.
        """
        xrefs = self.xrefs.filter(db_id=1).all()
        gff = '##gff-version 3\n'
        for xref in xrefs:
            gff += _xref_to_gff3_format(xref)
        return gff

    def get_ucsc_bed(self):
        """
        Format genomic coordinates from all xrefs into a single file in UCSC BED format.
        Example:
        chr1    29554    31097    RNA000063C361    0    +   29554    31097    255,0,0    3    486,104,122    0,1009,1421
        """
        xrefs = self.xrefs.filter(db_id=1).all()
        bed = ''
        for xref in xrefs:
            bed += _xref_to_bed_format(xref)
        return bed

    def get_description(self):
        """
        Get entry description.
        This function mimics the logic implemented in the xml dumping pipeline.
        See portal/management/commands/xml_exporters/rna2xml.py
        """
        def count_ena_xrefs():
            """
            Count xrefs from ENA.
            """
            return self.xrefs.filter(db__descr='ENA').count()

        def count_distinct_descriptions():
            """
            Count distinct description lines.
            """
            return self.xrefs.values_list('accession__description', flat=True).\
                              distinct().count()

        def get_distinct_products():
            """
            Get distinct non-null product values as a list.
            """
            return self.xrefs.values_list('accession__product', flat=True).\
                              filter(accession__product__isnull=False).\
                              distinct()

        def get_distinct_genes():
            """
            Get distinct non-null gene values as a list.
            """
            return self.xrefs.values_list('accession__gene', flat=True).\
                              filter(accession__gene__isnull=False).\
                              distinct()

        def get_distinct_feature_names():
            """
            Get distinct feature names as a list.
            """
            return self.xrefs.values_list('accession__feature_name',
                                          flat=True).distinct()

        def get_distinct_ncrna_classes():
            """
            For ncRNA features, get distinct ncrna_class values as a list.
            """
            return self.xrefs.values_list('accession__ncrna_class',
                                          flat=True).\
                              filter(accession__ncrna_class__isnull=False).\
                              distinct()

        def get_rna_type():
            """
            product > gene > feature name
            For ncRNA features, use ncrna_class annotations.
            """
            products = get_distinct_products()
            genes = get_distinct_genes()
            if len(products) == 1:
                rna_type = products[0]
            elif len(genes) == 1:
                rna_type = genes[0]
            else:
                feature_names = get_distinct_feature_names()
                if feature_names[0] == 'ncRNA' and len(feature_names) == 1:
                    ncrna_classes = get_distinct_ncrna_classes()
                    rna_type = '/'.join(ncrna_classes)
                else:
                    rna_type = '/'.join(feature_names)
            return rna_type

        num_ena_entries = count_ena_xrefs()
        num_distinct_descriptions = count_distinct_descriptions()
        if num_ena_entries == 1 or num_distinct_descriptions == 1:
            description_line = self.xrefs.all()[0].accession.description
            description_line = description_line[0].upper() + description_line[1:]
        else:
            distinct_species = self.count_distinct_organisms
            rna_type = get_rna_type()
            if distinct_species == 1:
                species = self.xrefs.all()[0].accession.species
                description_line = '{species} {rna_type}'.format(
                                    species=species, rna_type=rna_type)
            else:
                description_line = ('{rna_type} from '
                                    '{distinct_species} species').format(
                                    rna_type=rna_type,
                                    distinct_species=distinct_species)
        return description_line


class DatabaseStats(models.Model):
    """
    These data are kept in a separate table because accessing CLOBs is slow,
    and this table will only be loaded when necessary.
    """
    database = models.CharField(max_length=30, primary_key=True)
    length_counts = models.TextField()
    taxonomic_lineage = models.TextField()

    class Meta:
        db_table = 'rnc_database_json_stats'


class Database(models.Model):
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.CharField(max_length=30)
    current_release = models.IntegerField()
    full_descr = models.CharField(max_length=255)
    alive = models.CharField(max_length=1)
    for_release = models.CharField(max_length=1)
    display_name = models.CharField(max_length=40)
    url = models.CharField(max_length=100)
    project_id = models.CharField(max_length=10)
    avg_length = models.IntegerField()
    min_length = models.IntegerField()
    max_length = models.IntegerField()
    num_sequences = models.IntegerField()
    num_organisms = models.IntegerField()

    class Meta:
        db_table = 'rnc_database'

    def count_sequences(self):
        """
        Count unique sequences associated with the database.
        """
        return self.xrefs.values_list('upi', flat=True).distinct().count()

    def count_organisms(self):
        """
        Count distinct taxids associated with the database.
        """
        return self.xrefs.values_list('taxid', flat=True).distinct().count()

    def first_imported(self):
        """
        Get the earliest imported date.
        """
        return self.xrefs.order_by('timestamp').first().timestamp

    @cached_property
    def description(self):
        """
        Get database description.
        """
        return self.__get_database_attribute(self.display_name, 'description')

    @cached_property
    def label(self):
        """
        Get database slugified label.
        """
        return self.__get_database_attribute(self.display_name, 'label')

    @cached_property
    def examples(self):
        """
        Get database examples.
        """
        return self.__get_database_attribute(self.display_name, 'examples')

    def references(self):
        """
        Get literature references.
        """
        return self.__get_database_attribute(self.display_name, 'references')

    @cached_property
    def url(self):
        """
        Get database url.
        """
        return self.__get_database_attribute(self.display_name, 'url')

    @cached_property
    def abbreviation(self):
        """
        Get database name abbreviation.
        """
        return self.__get_database_attribute(self.display_name, 'abbreviation')

    def __get_database_attribute(self, db_name, attribute):
        """
        An accessor method for retrieving attributes from a list.
        """
        data = self.__get_database_data()
        return [x[attribute] for x in data if x['name'] == db_name].pop()

    def __get_database_data(self):
        """
        Some data about the databases should not be stored in the main database
        in order to make the update process easier.
        If references, examples, and descriptions are stored in the database,
        then each time a piece of data needs to be updated, one has to propagate
        the change across all databases, which is inconvenient and error prone.
        """
        return [
            {
                'name': 'ENA',
                'label': 'ena',
                'url': 'http://www.ebi.ac.uk/ena/',
                'description': "provides a comprehensive record of the world's nucleotide sequencing information",
                'abbreviation': 'European Nucleotide Archive',
                'examples': ['URS00002D0E0C', 'URS000035EE7E', 'URS0000000001'],
                'references': [
                    {
                        'title': 'Facing growth in the European Nucleotide Archive',
                        'authors': 'Cochrane G, Alako B, Amid C, Bower L, Cerdeno-Tarraga A, Cleland I, Gibson R, Goodgame N, Jang M, Kay S et al.',
                        'journal': 'Nucleic Acids Res. 2013 Jan;41(Database issue):D30-5',
                        'pubmed_id': 23203883,
                    },
                    {
                        'title': 'Assembly information services in the European Nucleotide Archive',
                        'authors': 'Pakseresht N, Alako B, Amid C, Cerdeno-Tarraga A, Cleland I, Gibson R, Goodgame N, Gur T, Jang M, Kay S et al.',
                        'journal': 'Nucleic Acids Res. 2014 Jan;42(Database issue):D38-43',
                        'pubmed_id': 24214989,
                    },
                ],
            },
            {
                'name': 'RFAM',
                'label': 'rfam',
                'url': 'http://rfam.xfam.org',
                'description': 'is a database containing information about ncRNA families and other structured RNA elements',
                'abbreviation': '',
                'examples': ['URS00000478B7', 'URS000066DAB6', 'URS000068EEC5'],
                'references': [
                    {
                        'title': 'Rfam 11.0: 10 years of RNA families',
                        'authors': 'Burge SW, Daub J, Eberhardt R, Tate J, Barquist L, Nawrocki EP, Eddy SR, Gardner PP, Bateman A',
                        'journal': 'Nucleic Acids Res. 2013 Jan;41(Database issue):D226-32',
                        'pubmed_id': 23125362,
                    },
                ],
            },
            {
                'name': 'miRBase',
                'label': 'mirbase',
                'url': 'http://www.mirbase.org/',
                'description': 'is a database of published miRNA sequences and annotations that provides a centralised system for assigning names to miRNA genes',
                'abbreviation': '',
                'examples': ['URS00003B7674', 'URS00003B7674', 'URS000016FD1A'],
                'references': [
                    {
                        'title': 'miRBase: integrating microRNA annotation and deep-sequencing data',
                        'authors': 'Kozomara A., Griffiths-Jones S.',
                        'journal': 'Nucleic Acids Res. 39(Database issue): D152-7 (2011 Jan)',
                        'pubmed_id': 21037258,
                    },
                ],
            },
            {
                'name': 'VEGA',
                'label': 'vega',
                'url': 'http://vega.sanger.ac.uk/',
                'description': 'is a repository for high-quality gene models produced by the manual annotation of vertebrate genomes',
                'abbreviation': 'Vertebrate Genome Annotation',
                'examples': ['URS00000B15DA', 'URS00000A54A6', 'URS00003B2BEF'],
                'references': [
                    {
                        'title': 'The GENCODE v7 catalog of human long noncoding RNAs: analysis of their gene structure, evolution, and expression.',
                        'authors': 'Derrien T., Johnson R., Bussotti G., Tanzer A., Djebali S., Tilgner H., Guernec G., Martin D., Merkel A., Knowles DG. et al.',
                        'journal': 'Genome Res. 22(9): 1775-1789 (2012 Sep)',
                        'pubmed_id': 22955988,
                    },
                    {
                        'title': 'GENCODE: the reference human genome annotation for The ENCODE Project',
                        'authors': 'Harrow J., Frankish A., Gonzalez JM., Tapanari E., Diekhans M., Kokocinski F., Aken BL., Barrell D., Zadissa A., Searle S. et al.',
                        'journal': 'Genome Res. 22(9): 1760-1774 (2012 Sep)',
                        'pubmed_id': 22955987,
                    },
                ],
            },
            {
                'name': 'tmRNA Website',
                'label': 'tmrna-website',
                'url': 'http://bioinformatics.sandia.gov/tmrna/',
                'description': 'contains predicted tmRNA sequences from RefSeq prokaryotic genomes, plasmids and phages',
                'abbreviation': '',
                'examples': ['URS000060F5B3', 'URS000058C344', 'URS000048A91D'],
                'references': [
                    {
                        'title': 'The tmRNA website: reductive evolution of tmRNA in plastids and other endosymbionts',
                        'authors': 'Gueneau de Novoa P., Williams KP.',
                        'journal': 'Nucleic Acids Res. 32(Database issue): D104-8 (2004 Jan)',
                        'pubmed_id': 14681369,
                    },
                ],
            },
            {
                'name': 'SRPDB',
                'label': 'srpdb',
                'url': 'http://rnp.uthscsa.edu/rnp/SRPDB/SRPDB.html',
                'description': 'provides aligned, annotated and phylogenetically ordered sequences related to structure and function of SRP',
                'abbreviation': 'Signal Recognition Particle Database',
                'examples': ['URS00000478B7', 'URS00001C03DC', 'URS00005C64FE'],
                'references': [
                    {
                        'title': 'Kinship in the SRP RNA family',
                        'authors': 'Rosenblad MA., Larsen N., Samuelsson T., Zwieb C.',
                        'journal': 'RNA Biol 6(5): 508-516 (2009 Nov-Dec)',
                        'pubmed_id': 19838050,
                    },
                    {
                        'title': 'The tmRDB and SRPDB resources',
                        'authors': 'Andersen ES., Rosenblad MA., Larsen N., Westergaard JC., Burks J., Wower IK., Wower J., Gorodkin J., Samuelsson T., Zwieb C.',
                        'journal': 'Nucleic Acids Res. 34(Database issue): D163-8 (2006 Jan)',
                        'pubmed_id': 16381838,
                    },
                ],
            },
            {
                'name': 'lncRNAdb',
                'label': 'lncrnadb',
                'url': 'http://lncrnadb.org/',
                'description': 'is a database providing comprehensive annotations of eukaryotic long non-coding RNAs (lncRNAs)',
                'abbreviation': '',
                'examples': ['URS00000478B7', 'URS00005E1511', 'URS0000147018'],
                'references': [
                    {
                        'title': 'lncRNAdb: a reference database for long noncoding RNAs',
                        'authors': 'Amaral P.P., Clark M.B., Gascoigne D.K., Dinger M.E., Mattick J.S.',
                        'journal': 'Nucleic Acids Res. 39(Database issue):D146-D151(2011)',
                        'pubmed_id': '21112873',
                    },
                ],
            },
            {
                'name': 'gtRNAdb',
                'label': 'gtrnadb',
                'url': 'http://gtrnadb.ucsc.edu/',
                'description': 'contains tRNA gene predictions on complete or nearly complete genomes',
                'abbreviation': '',
                'examples': ['URS000047C79B', 'URS00006725C9', 'URS00001F9D54'],
                'references': [
                    {
                        'title': 'GtRNAdb: a database of transfer RNA genes detected in genomic sequence',
                        'authors': 'Chan P.P., Lowe T.M.',
                        'journal': 'Nucleic Acids Res. 37(Database issue):D93-D97(2009)',
                        'pubmed_id': 18984615,
                    },
                ],
            },
            {
                'name': 'RefSeq',
                'label': 'refseq',
                'url': 'http://www.ncbi.nlm.nih.gov/refseq/',
                'description': 'is a comprehensive, integrated, non-redundant, well-annotated set of reference sequences',
                'abbreviation': 'NCBI Reference Sequence Database',
                'examples': ['URS000075D2CB', 'URS000075A08B'],
                'references': [
                    {
                        'title': 'RefSeq: an update on mammalian reference sequences.',
                        'authors': 'Pruitt K.D., Brown G.R., Hiatt S.M., Thibaud-Nissen F., Astashyn A., Ermolaeva O., Farrell C.M., Hart J., Landrum M.J., McGarvey K.M. et al.',
                        'journal': 'Nucleic Acids Res. 2014 Jan;42(Database issue):D756-63',
                        'pubmed_id': '24259432',
                    },
                ],
            },
        ]

class Release(models.Model):
    db = models.ForeignKey(Database, db_column='dbid', related_name='db')
    release_date = models.DateField()
    release_type = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.TextField()
    force_load = models.CharField(max_length=1)

    def get_release_type(self):
        return 'full' if self.release_type == 'F' else 'incremental'

    class Meta:
        db_table = 'rnc_release'


class Accession(models.Model):
    accession = models.CharField(max_length=100, primary_key=True)
    parent_ac = models.CharField(max_length=100)
    seq_version = models.IntegerField()
    feature_start = models.IntegerField()
    feature_end = models.IntegerField()
    feature_name = models.CharField(max_length=20)
    ordinal = models.IntegerField()
    division = models.CharField(max_length=3)
    keywords = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    species = models.CharField(max_length=150)
    organelle = models.CharField(max_length=100)
    classification = models.CharField(max_length=500)
    project = models.CharField(max_length=50)
    is_composite = models.CharField(max_length=1)
    non_coding_id = models.CharField(max_length=100)
    database = models.CharField(max_length=20)
    external_id = models.CharField(max_length=150)
    optional_id = models.CharField(max_length=100)
    anticodon = models.CharField(max_length=50)
    experiment = models.CharField(max_length=500)
    function = models.CharField(max_length=500)
    gene = models.CharField(max_length=50)
    gene_synonym = models.CharField(max_length=400)
    inference = models.CharField(max_length=100)
    locus_tag = models.CharField(max_length=50)
    genome_position = models.CharField(max_length=200, db_column='map')
    mol_type = models.CharField(max_length=50)
    ncrna_class = models.CharField(max_length=50)
    note = models.CharField(max_length=1500)
    old_locus_tag = models.CharField(max_length=50)
    product = models.CharField(max_length=300)
    db_xref = models.CharField(max_length=100)

    class Meta:
        db_table = 'rnc_accessions'

    def get_biotype(self):
        """
        Biotype annotations are stored in notes and come from Ensembl and VEGA
        entries.
        Biotype is used to color entries in Genoverse.
        If biotype contains the word "RNA" it is given a predefined color.
        """
        biotype = 'ncRNA' # default biotype
        match = re.search(r'biotype\:(\w+)', self.note)
        if match:
            biotype = match.group(1)
        return biotype

    def get_rna_type(self):
        """
        Get the type of RNA, which either the name of the feature from the
        feature table in the Non-coding product, or for `ncRNA` features,
        it's one of the ncRNA classes defined by INSDC.
        """
        if self.feature_name == 'ncRNA':
            return self.ncrna_class
        else:
            return self.feature_name

    def get_srpdb_id(self):
        return re.sub('\.\d+$', '', self.external_id)

    def get_ena_url(self):
        """
        Get the ENA entry url that refers to the entry from
        the Non-coding product containing the cross-reference.
        """
        if self.database == 'RFAM':
            return '' # no source links for RFAM entries
        ena_base_url = "http://www.ebi.ac.uk/ena/data/view/Non-coding:"
        if self.is_composite == 'Y':
            return ena_base_url + self.non_coding_id
        else:
            return ena_base_url + self.accession

    def get_expert_db_external_url(self):
        """
        Get external url to expert database.
        """
        urls = {
            'RFAM': 'http://rfam.xfam.org/family/',
            'SRPDB': 'http://rnp.uthscsa.edu/rnp/SRPDB/rna/sequences/fasta/',
            'VEGA': 'http://vega.sanger.ac.uk/Homo_sapiens/Gene/Summary?db=core;g=',
            'MIRBASE': 'http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=',
            'TMRNA_WEB': 'http://bioinformatics.sandia.gov/tmrna/seqs/',
            'LNCRNADB': 'http://www.lncrnadb.org/Detail.aspx?TKeyID=',
            'GTRNADB': 'http://lowelab.ucsc.edu/GtRNAdb/',
            'REFSEQ': 'http://www.ncbi.nlm.nih.gov/nuccore/',
        }
        if self.database in urls.keys():
            return urls[self.database] + self.external_id
        else:
            return ''


class GenomicCoordinates(models.Model):
    accession = models.ForeignKey('Accession', db_column='accession', to_field='accession', related_name='coordinates')
    primary_accession = models.CharField(max_length=50)
    local_start = models.IntegerField()
    local_end = models.IntegerField()
    chromosome = models.CharField(max_length=50, db_column='name')
    primary_start = models.IntegerField()
    primary_end = models.IntegerField()
    strand = models.IntegerField()

    class Meta:
        db_table = 'rnc_coordinates'


class Xref(models.Model):
    db = models.ForeignKey(Database, db_column='dbid', related_name='xrefs')
    accession = models.ForeignKey(Accession, db_column='ac', to_field='accession', related_name='xrefs', unique=True)
    created = models.ForeignKey(Release, db_column='created', related_name='release_created')
    last = models.ForeignKey(Release, db_column='last', related_name='last_release')
    upi = models.ForeignKey(Rna, db_column='upi', to_field='upi', related_name='xrefs')
    version_i = models.IntegerField()
    deleted = models.CharField(max_length=1)
    timestamp = models.DateTimeField()
    userstamp = models.CharField(max_length=100)
    version = models.IntegerField()
    taxid = models.IntegerField()

    class Meta:
        db_table = 'xref'

    def is_rfam_seed(self):
        """
        Determine whether an xref is part of a manually curated
        RFAM seed alignment.
        """
        if re.search('alignment\:seed', self.accession.note, re.IGNORECASE) is not None:
            return True
        else:
            return False

    def get_ncbi_gene_id(self):
        """
        GeneID links are stored in the db_xref field.
        """
        match = re.search('GeneID\:(\d+)', self.accession.db_xref, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            return None

    def get_ucsc_bed(self):
        """
        Format genomic coordinates in BED format.
        """
        return _xref_to_bed_format(self)

    def get_gff(self):
        """
        Format genomic coordinates in GFF format.
        """
        return _xref_to_gff_format(self)

    def get_gff3(self):
        """
        Format genomic coordinates in GFF3 format.
        """
        return _xref_to_gff3_format(self)

    def is_refseq_mirna(self):
        """
        RefSeq miRNAs are stored in 3 xrefs:
            * precursor_RNA
            * 5-prime ncRNA
            * 3-prime ncRNA
        which share the same parent accession.
        """
        same_parent = Accession.objects.filter(parent_ac=self.accession.parent_ac).all()
        if len(same_parent) > 1:
            return True
        else:
            return False

    def get_refseq_mirna_precursor(self):
        """
        Given a 5-prime or 3-prime mature product, retrieve its precursor miRNA.
        """
        if self.accession.feature_name != 'precursor_RNA':
            rna = Xref.objects.filter(accession__parent_ac=self.accession.parent_ac,
                                      accession__feature_name='precursor_RNA').\
                               first()
            return rna.upi
        else:
            return None

    def get_refseq_mirna_mature_products(self):
        """
        Given a precursor miRNA, retrieve its mature products.
        """
        mature_products = Xref.objects.filter(accession__parent_ac=self.accession.parent_ac,
                                              accession__feature_name='ncRNA').\
                                       all()
        upis = []
        for mature_product in mature_products:
            upis.append(mature_product.upi)
        return upis

    def get_vega_splice_variants(self):
        splice_variants = []
        if self.db.display_name != 'VEGA':
            return splice_variants
        for splice_variant in Accession.objects.filter(external_id=self.accession.external_id).\
                                                exclude(accession=self.accession.accession).\
                                                all():
            for splice_xref in splice_variant.xrefs.all():
                splice_variants.append(splice_xref.upi)
            splice_variants.sort(key=lambda x: x.length)
        return splice_variants

    def get_tmrna_mate_upi(self):
        """
        Get the mate of the 2-piece tmRNA
        """
        if self.db.display_name != 'tmRNA Website':
            tmrna_mate_upi = False
        if not self.accession.optional_id:  # no mate info
            tmrna_mate_upi = False
        mate = Accession.objects.filter(parent_ac=self.accession.optional_id, is_composite='Y').get()
        tmrna_mate_upi = mate.xrefs.get().upi.upi
        return tmrna_mate_upi

    def get_tmrna_type(self):
        """
        Possible tmRNA types:
            * acceptor (tRNA-like domain)
            * coding (mRNA-like domain),
            * precursor (contains the acceptor and coding sequences and other intervening sequences)
        """
        tmrna_type = 0
        if self.db.display_name != 'tmRNA Website':
            tmrna_type = 0 # not tmRNA
        if not self.accession.optional_id:
            tmrna_type = 1 # one-piece or precursor
        else:
            tmrna_type = 2 # two-piece tmRNA
        return tmrna_type

    def get_ensembl_species_name(self):
        """
        Get a species name that can be used in Ensembl urls.
        """
        return self.accession.species.replace(' ', '_').lower()

    def get_ucsc_db_id(self):
        """
        Get UCSC id for the genome assembly.
        http://genome.ucsc.edu/FAQ/FAQreleases.html
        """
        ucsc_db_ids = {
            9606: 'hg19', # human
        }
        if self.taxid in ucsc_db_ids.keys():
            return ucsc_db_ids[self.taxid]
        else:
            return None

    def new_has_genomic_coordinates(self):
        """
        Mirror the existing API while using the new GenomicCoordinates model.
        TODO: remove "new_" from the method name.
        """
        return True if self.accession.coordinates.first() and self.accession.coordinates.first().chromosome else False

    def new_get_genomic_coordinates(self):
        """
        Mirror the existing API while using the new GenomicCoordinates model.
        TODO: remove "new_" from the method name.
        """
        return {
            'chromosome': self.get_feature_chromosome(),
            'strand': self.get_feature_strand(),
            'start': self.get_feature_start(),
            'end': self.get_feature_end(),
        }

    def get_feature_chromosome(self):
        """
        Get the chromosome name for the genomic location.
        The name represents a toplevel accession as defined
        by the Ensembl API and can include patch/scaffold names etc.
        """
        return self.accession.coordinates.first().chromosome

    def get_feature_strand(self):
        """
        Return 1 or -1 to indicate the forward and reverse strands respectively.
        """
        return self.accession.coordinates.first().strand

    def get_feature_start(self):
        """
        Get the `start` coordinates of the genomic feature.
        """
        data = self.accession.coordinates.aggregate(min_feature_start = Min('primary_start'))
        return data['min_feature_start']

    def get_feature_end(self):
        """
        Get the `end` coordinates of the genomic feature.
        """
        data = self.accession.coordinates.aggregate(max_feature_end = Max('primary_end'))
        return data['max_feature_end']


    def has_genomic_coordinates(self):
        """
        True for sequences with genomic coordinates.
        """
        return True if self.accession.assembly.count() > 0 else False

    def get_genomic_coordinates(self):
        """
        """
        data = {
            'chromosome': self.get_assembly_chromosome(),
            'strand': self.get_assembly_strand(),
            'start': self.get_assembly_start(),
            'end': self.get_assembly_end()
        }
        return data

    def get_assembly_start(self):
        """
        Select the minimum starting coordinates to account for complementary strands.
        """
        data = self.accession.assembly.aggregate(assembly_start = Min('primary_start'))
        return data['assembly_start']

    def get_assembly_end(self):
        """
        Select the maximum ending coordinates to account for complementary strands.
        """
        data = self.accession.assembly.aggregate(assembly_end = Max('primary_end'))
        return data['assembly_end']

    def get_assembly_chromosome(self):
        """
        Get the chromosome for the genomic coordinates.
        """
        return self.accession.assembly.first().chromosome.chromosome

    def get_assembly_strand(self):
        """
        Get the strand for the genomic coordinates.
        """
        return self.accession.assembly.first().strand


class Chromosome(models.Model):
    ena_accession = models.CharField(max_length=20, db_column='assembly', primary_key=True)
    chromosome = models.CharField(max_length=2)

    class Meta:
        db_table = 'rnc_chromosome'


class Assembly(models.Model):
    accession = models.ForeignKey(Accession, db_column='accession', to_field='accession', related_name='assembly')
    chromosome = models.ForeignKey(Chromosome, db_column='primary_identifier', to_field='ena_accession', related_name='genome')
    local_start = models.IntegerField()
    local_end = models.IntegerField()
    primary_start = models.IntegerField()
    primary_end = models.IntegerField()
    strand = models.IntegerField()

    class Meta:
        db_table = 'rnc_assembly'


class Reference(models.Model):
    authors = models.TextField()
    location = models.CharField(max_length=4000)
    title = models.CharField(max_length=4000)
    pubmed = models.CharField(max_length=10, db_column='pmid')
    doi = models.CharField(max_length=80)

    def get_title(self):
        title = self.title
        if self.location[:9] == 'Submitted':
            title = 'INSDC submission'
        else:
            title = title if title else 'No title available'
        return title

    class Meta:
        db_table = 'rnc_references'


class Reference_map(models.Model):
    accession = models.ForeignKey(Accession, db_column='accession', to_field='accession', related_name='refs')
    data = models.ForeignKey(Reference, db_column='reference_id')

    class Meta:
        db_table = 'rnc_reference_map'

"""
Common auxiliary functions.
"""
def _xref_to_gff_format(xref):
    """
    Return genome coordinates of an xref in GFF format. Available in Rna and Xref models.
    """
    gff = ''
    assemblies = xref.accession.assembly.select_related('chromosome').all()
    if assemblies.count() == 0:
        return gff
    for assembly in assemblies:
        gff += "chr%s\tRNAcentral\texon\t%s\t%s\t.\t%s\t.\t%s\n" % (assembly.chromosome.chromosome,
                                                                    assembly.primary_start,
                                                                    assembly.primary_end,
                                                                    '+' if assembly.strand > 0 else '-',
                                                                    xref.upi.upi)
    return gff

def _xref_to_gff3_format(xref):
    """
    Return genome coordinates of an xref in GFF3 format. Available in Rna and Xref models.
    """
    gff = ''
    assemblies = xref.accession.assembly.select_related('chromosome').all()
    if assemblies.count() == 0:
        return gff
    for i, assembly in enumerate(assemblies):
        seqid = assembly.chromosome.chromosome
        source = 'RNAcentral'
        seq_type = 'noncoding_exon'
        start = assembly.primary_start
        end = assembly.primary_end
        score = '.'
        strand = '+' if assembly.strand > 0 else '-'
        phase = '.'
        attributes = {
            'ID': '_'.join([xref.accession.accession, 'exon' + str(i+1)]),
            'Name': xref.upi.upi,
        }
        attributes_joined = ';'.join("%s=%s" % t for t in attributes.iteritems())
        gff += "%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n" % (seqid,
                                                           source,
                                                           seq_type,
                                                           start,
                                                           end,
                                                           score,
                                                           strand,
                                                           phase,
                                                           attributes_joined
                                                           )
    return gff

def _xref_to_bed_format(xref):
    """
    Return genome coordinates of an xref in BED format. Available in Rna and Xref models.
    """
    bed = ''
    assemblies = xref.accession.assembly.select_related('chromosome').order_by('primary_start').all()
    if assemblies.count() == 0:
        return bed
    # prepare fields
    chromosome = assemblies[0].chromosome.chromosome
    chrom_start = xref.get_assembly_start()
    chrom_end = xref.get_assembly_end()
    upi = xref.upi.upi
    score = 0
    strand = '+' if assemblies[0].strand > 0 else '-'
    thick_start = chrom_start
    thick_end = chrom_end
    item_rgb = "63,125,151"
    block_count = assemblies.count()
    block_sizes = []
    block_starts = []
    for i, exon in enumerate(assemblies):
        block_sizes.append(exon.primary_end - exon.primary_start)
        if i == 0:
            block_starts.append(0)
        else:
            block_starts.append(exon.primary_start - assemblies[0].primary_start)
    bed = "chr%s\t%i\t%i\t%s\t%i\t%s\t%i\t%i\t%s\t%i\t%s\t%s\n" % (chromosome,
                                                                   chrom_start,
                                                                   chrom_end,
                                                                   upi,
                                                                   score,
                                                                   strand,
                                                                   thick_start,
                                                                   thick_end,
                                                                   item_rgb,
                                                                   block_count,
                                                                   ','.join(map(str,block_sizes)),
                                                                   ','.join(map(str,block_starts))
                                                                   )
    return bed
