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
import re

# to make text fields searchable, add character set functional indexes in Oracle
# CREATE INDEX index_name ON table_name(SYS_OP_C2C(column_name));


class Rna(models.Model):
    upi = models.CharField(max_length=13, unique=True, db_index=True)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
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

    class Meta:
        db_table = 'rnc_release'


class Accessions(models.Model):
    accession = models.CharField(max_length=100, unique=True)
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


class Xref(models.Model):
    db = models.ForeignKey(Database, db_column='dbid')
    accession = models.ForeignKey(Accessions, db_column='ac', to_field='accession', related_name='xrefs', unique=True)
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
        for splice_variant in Accessions.objects.filter(external_id=self.accession.external_id).\
                                                 exclude(accession=self.accession.accession).\
                                                 all():
            for splice_xref in splice_variant.xrefs.all():
                rnac = splice_xref.upi
                rnac.upi = rnac.upi.replace('UPI', 'RNS')
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
        mate = Accessions.objects.filter(parent_ac=self.accession.optional_id, is_composite='Y').get()
        tmrna_mate_upi = mate.xrefs.get().upi.upi.replace('UPI', 'RNS')
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


class Reference(models.Model):
    authors = models.TextField()
    location = models.CharField(max_length=4000)
    title = models.CharField(max_length=4000)
    pubmed = models.CharField(max_length=10, db_column='pmid')
    doi = models.CharField(max_length=80)

    class Meta:
        db_table = 'rnc_references'


class Reference_map(models.Model):
    accession = models.ForeignKey(Xref, db_column='accession', to_field='accession', related_name='refs')
    data = models.ForeignKey(Reference, db_column='reference_id')

    class Meta:
        db_table = 'rnc_reference_map'
