from django.db import models

# Create your models here.
class Rna(models.Model):
    upi = models.CharField(max_length=200)
    timestamp = models.CharField(max_length=10)
    userstamp = models.CharField(max_length=100)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    seq_short = models.CharField(max_length=4000)
    seq_long = models.TextField()
    md5 = models.CharField(max_length=32)

    class Meta:
        db_table = 'rna'

class Xref(models.Model):
	dbid = models.IntegerField()
	created = models.IntegerField()
	last = models.IntegerField()
	upi = models.ForeignKey(Rna)
	version_i = models.IntegerField()
	deleted = models.CharField(max_length=1)
	timestamp = models.DateTimeField()
	userstamp = models.CharField(max_length=100)
	ac = models.CharField(max_length=150)
	version = models.IntegerField()
	taxid = models.IntegerField()

	class Meta:
		db_table = 'xref'
