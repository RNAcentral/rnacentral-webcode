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
        if self.seq_short:
            return self.seq_short.replace('T', 'U').upper()
        else:
            return self.seq_long.replace('T', 'U').upper()

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
        Get xrefs only from the expert database.
        """
        return self.xrefs.select_related().exclude(accession__is_composite='N').all()

    def get_ena_xrefs(self):
        """
        Get ENA xrefs that don't have corresponding expert database entries.
        """
        expert_db_projects = [db.project_id for db in Database.objects.exclude(project_id=None).all()]
        return self.xrefs.filter(db__descr='ENA').exclude(accession__project__in=expert_db_projects).select_related().all()

    def get_xrefs(self):
        """
        Concatenate querysets putting the expert database xrefs
        at the beginning of the resulting queryset.
        """
        return self.get_ena_xrefs() | self.get_expert_database_xrefs()

    def count_distinct_organisms(self):
        return self.xrefs.values('taxid').distinct().count()

    def count_distinct_databases(self):
        return self.xrefs.values('db_id').distinct().count()

    def first_seen(self):
        data = self.xrefs.aggregate(first_seen=Min('created__release_date'))
        return data['first_seen']

    def last_seen(self):
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
        fasta = "> %s\n%s" % (self.upi, split_seq)
        return fasta


class Database(models.Model):
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.CharField(max_length=30)
    current_release = models.IntegerField()
    full_descr = models.CharField(max_length=255)
    alive = models.CharField(max_length=1)
    for_release = models.CharField(max_length=1)
    display_name = models.CharField(max_length=40)
    logo = models.CharField(max_length=50)
    url = models.CharField(max_length=100)
    project_id = models.CharField(max_length=10)

    class Meta:
        db_table = 'rnc_database'


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
    external_id = models.CharField(max_length=100)
    optional_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'rnc_accessions'

    def get_srpdb_id(self):
        return re.sub('\.\d+$', '', self.external_id)

    def get_ena_url(self):
        """
        Get the ENA entry url that refers to the entry from
        the Non-coding product containing the cross-reference.
        """
        ena_base_url = "http://www.ebi.ac.uk/ena/data/view/Non-coding:"
        if self.is_composite == 'Y':
            return ena_base_url + self.non_coding_id
        else:
            return ena_base_url + self.accession

    def get_expert_db_external_url(self):
        """
        Get the external url to the expert database.
        """
        if self.database == 'RFAM':
            base_url = "http://rfam.sanger.ac.uk/family/"
        elif self.database == 'SRPDB':
            base_url = "http://rnp.uthscsa.edu/rnp/SRPDB/rna/sequences/fasta/"
        elif self.database == 'VEGA':
            base_url = "http://vega.sanger.ac.uk/Homo_sapiens/Gene/Summary?db=core;g="
        elif self.database == 'MIRBASE':
            base_url = "http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc="
        elif self.database == 'TMRNA_WEB':
            base_url = "http://bioinformatics.sandia.gov/tmrna/seqs/"
        else:
            return ""
        return base_url + self.external_id


class Xref(models.Model):
    db = models.ForeignKey(Database, db_column='dbid')
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

    def get_vega_splice_variants(self):
        splice_variants = []
        if self.db.display_name != 'VEGA':
            return splice_variants
        for splice_variant in Accession.objects.filter(external_id=self.accession.external_id).\
                                                 exclude(accession=self.accession.accession).\
                                                 all():
            for splice_xref in splice_variant.xrefs.all():
                rnac = splice_xref.upi
                rnac.upi = rnac.upi
                splice_variants.append(rnac)
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
