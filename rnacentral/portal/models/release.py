from caching.base import CachingMixin, CachingManager
from django.db import models

from portal.models.database import Database


class Release(CachingMixin, models.Model):
    db = models.ForeignKey(Database, db_column='dbid', related_name='db')
    release_date = models.DateField()
    release_type = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.TextField()
    force_load = models.CharField(max_length=1)

    objects = CachingManager()

    def get_release_type(self):
        return 'full' if self.release_type == 'F' else 'incremental'

    class Meta:
        db_table = 'rnc_release'