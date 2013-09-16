from django.db import models

# Create your models here.
class Rna(models.Model):
    upi = models.CharField(max_length=200, primary_key=True)
    timestamp = models.CharField(max_length=10)
    userstamp = models.CharField(max_length=100)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    seq_short = models.CharField(max_length=4000)
    seq_long = models.TextField()
    md5 = models.CharField(max_length=32)

    class Meta:
        db_table = 'rna'

    def get_sequence(self):
    	if self.seq_short:
    		return self.seq_short
    	else:
    		return self.seq_long


class Xref(models.Model):
	id = models.IntegerField(primary_key=True)
	dbid = models.IntegerField()
	created = models.IntegerField()
	last = models.IntegerField()
	upi = models.ForeignKey(Rna, db_column='UPI')
	version_i = models.IntegerField()
	deleted = models.CharField(max_length=1)
	timestamp = models.DateTimeField()
	userstamp = models.CharField(max_length=100)
	ac = models.CharField(max_length=150)
	version = models.IntegerField()
	taxid = models.IntegerField()

	class Meta:
		db_table = 'xref'
