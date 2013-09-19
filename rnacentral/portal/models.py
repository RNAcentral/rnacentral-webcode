from django.db import models

class Rna(models.Model):
    upi = models.CharField(primary_key=True, max_length=13)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    seq_short = models.CharField(max_length=4000)
    seq_long = models.TextField()
    md5 = models.CharField(max_length=32)

    class Meta:
        db_table = 'rnc_rna'

    def get_sequence(self):
    	if self.seq_short:
    		return self.seq_short
    	else:
    		return self.seq_long


class Database(models.Model):
    id = models.IntegerField(primary_key=True)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.TextField()
    current_release = models.IntegerField()
    full_descr = models.CharField(max_length=255)
    alive = models.CharField(max_length=1)
    for_release = models.CharField(max_length=1)
    display_name = models.CharField(max_length=40)

    class Meta:
        db_table = 'rnc_database'


class Release(models.Model):
    id = models.IntegerField(primary_key=True)
    db = models.ForeignKey(Database, db_column='db_id', related_name='db')
    release_date = models.DateField()
    release_type = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.TextField()
    force_load = models.CharField(max_length=1)

    class Meta:
        db_table = 'rnc_release'


class Ac(models.Model):
    id = models.CharField(db_column='ac', max_length=100, primary_key=True)
    parent_ac = models.CharField(max_length=100)
    seq_version = models.IntegerField()
    feature_start = models.IntegerField()
    feature_end = models.IntegerField()
    feature_name = models.CharField(max_length=40)
    ordinal = models.CharField(max_length=40)
    division = models.CharField(max_length=3)
    keywords = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    species = models.CharField(max_length=100)
    organelle = models.CharField(max_length=100)
    classification = models.CharField(max_length=500)
    project = models.CharField(max_length=50)

    class Meta:
        db_table = 'rnc_accession_info'


class Xref(models.Model):
    id = models.IntegerField(primary_key=True)
    db = models.ForeignKey(Database, db_column='db_id')
    created = models.ForeignKey(Release, db_column='created', related_name='release_created')
    last = models.ForeignKey(Release, db_column='last', related_name='last_release')
    upi = models.ForeignKey(Rna, db_column='UPI', related_name='xrefs')
    version_i = models.IntegerField()
    deleted = models.CharField(max_length=1)
    timestamp = models.DateTimeField()
    userstamp = models.CharField(max_length=100)
    accession = models.ForeignKey(Ac, db_column='accession', blank=True, null=True)
    version = models.IntegerField()
    taxid = models.IntegerField()

    class Meta:
        db_table = 'rnc_xref'


class CompositeId(models.Model):
    composite_id = models.CharField(max_length=100, primary_key=True)
    ac = models.ForeignKey(Ac, to_field='id')
    database = models.CharField(max_length=20)
    optional_id = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'rnc_composite_ids'