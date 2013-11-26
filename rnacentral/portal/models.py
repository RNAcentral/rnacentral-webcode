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
    accession = models.ForeignKey(Accessions, db_column='ac', to_field='accession', related_name='xrefs')
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


class Reference(models.Model):
    rna = models.ForeignKey(Rna, db_column='md5', to_field = 'md5', related_name='refs')
    authors_md5 = models.CharField(max_length=32)
    authors = models.TextField()
    location = models.CharField(max_length=4000)
    title = models.CharField(max_length=4000)
    pubmed = models.CharField(max_length=10)
    doi = models.CharField(max_length=80)
    publisher = models.CharField(max_length=128)
    editors = models.CharField(max_length=250)

    class Meta:
        db_table = 'rnc_references'
