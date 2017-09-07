from caching.base import CachingMixin, CachingManager
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property

from portal.config.expert_databases import expert_dbs as rnacentral_expert_dbs


class Database(CachingMixin, models.Model):
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

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_database'

    def count_sequences(self):
        """Count unique sequences associated with the database."""
        return self.xrefs.filter(deleted='N').values_list('upi', 'taxid').distinct().count()

    def count_organisms(self):
        """Count distinct taxids associated with the database."""
        return self.xrefs.values_list('taxid', flat=True).distinct().count()

    def first_imported(self):
        """Get the earliest imported date."""
        return self.xrefs.order_by('timestamp').first().timestamp

    @cached_property
    def description(self):
        """Get database description."""
        return self.__get_database_attribute(self.display_name, 'description')

    @cached_property
    def label(self):
        """Get database slugified label."""
        return self.__get_database_attribute(self.display_name, 'label')

    @cached_property
    def examples(self):
        """Get database examples."""
        return self.__get_database_attribute(self.display_name, 'examples')

    def references(self):
        """Get literature references."""
        return self.__get_database_attribute(self.display_name, 'references')

    @cached_property
    def url(self):
        """Get database url."""
        return self.__get_database_attribute(self.display_name, 'url')

    @cached_property
    def abbreviation(self):
        """Get database name abbreviation."""
        return self.__get_database_attribute(self.display_name, 'abbreviation')

    @cached_property
    def name(self):
        """
        Get database display name. This is safer than using self.display_name
        because it doesn't require updating the database field.
        """
        return self.__get_database_attribute(self.display_name, 'name')

    @cached_property
    def status(self):
        """Get the status of the database (new/updated/etc)."""
        return self.__get_database_attribute(self.display_name, 'status')

    @cached_property
    def imported(self):
        """Get the status of the database (new/updated/etc)."""
        return self.__get_database_attribute(self.display_name, 'imported')

    @cached_property
    def version(self):
        """Get database version (Rfam 12, PDB as of date etc)."""
        return self.__get_database_attribute(self.display_name, 'version')

    def __get_database_attribute(self, db_name, attribute):
        """An accessor method for retrieving attributes from a list."""
        return [x[attribute] for x in rnacentral_expert_dbs if x['name'].lower() == db_name.lower()].pop()

    def get_absolute_url(self):
        """Get a URL for a Database object. Used for generating sitemaps."""
        return reverse('expert-database', kwargs={'expert_db_name': self.label})