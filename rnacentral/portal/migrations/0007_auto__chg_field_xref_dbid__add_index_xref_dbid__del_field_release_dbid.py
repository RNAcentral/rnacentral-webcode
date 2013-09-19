# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'Xref.dbid' to match new field type.
        db.rename_column('xref_myisam', 'dbid', 'db_id')
        # Changing field 'Xref.dbid'
        db.alter_column('xref_myisam', 'id', self.gf('django.db.models.fields.related.ForeignKey')(primary_key=True, db_column='id', to=orm['portal.Release']))
        # Adding index on 'Xref', fields ['dbid']
        db.create_index('xref_myisam', ['id'])

        # Deleting field 'Release.dbid'
        db.delete_column('rnc_release', 'dbid')

        # Adding field 'Release.db'
        db.add_column('rnc_release', 'db',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='db', to=orm['portal.Database']),
                      keep_default=False)


    def backwards(self, orm):
        # Removing index on 'Xref', fields ['dbid']
        db.delete_index('xref_myisam', ['id'])


        # Renaming column for 'Xref.dbid' to match new field type.
        db.rename_column('xref_myisam', 'id', 'db_id')
        # Changing field 'Xref.dbid'
        db.alter_column('xref_myisam', 'db_id', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'Release.dbid'
        raise RuntimeError("Cannot reverse this migration. 'Release.dbid' and its values cannot be restored.")

        # The following code is provided here to aid in writing a correct migration        # Adding field 'Release.dbid'
        db.add_column('rnc_release', 'dbid',
                      self.gf('django.db.models.fields.IntegerField')(),
                      keep_default=False)

        # Deleting field 'Release.db'
        db.delete_column('rnc_release', 'db_id')


    models = {
        u'portal.ac': {
            'Meta': {'object_name': 'Ac', 'db_table': "'rnc_ac_info'"},
            'ac': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'classification': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'division': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'feature_end': ('django.db.models.fields.IntegerField', [], {}),
            'feature_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'feature_start': ('django.db.models.fields.IntegerField', [], {}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ordinal': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'organelle': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent_ac': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'seq_version': ('django.db.models.fields.IntegerField', [], {}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'portal.database': {
            'Meta': {'object_name': 'Database', 'db_table': "'rnc_database'"},
            'alive': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'current_release': ('django.db.models.fields.IntegerField', [], {}),
            'descr': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'for_release': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'full_descr': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateField', [], {}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'portal.release': {
            'Meta': {'object_name': 'Release', 'db_table': "'rnc_release'"},
            'db': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'db'", 'to': u"orm['portal.Database']"}),
            'descr': ('django.db.models.fields.TextField', [], {}),
            'force_load': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'release_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'timestamp': ('django.db.models.fields.DateField', [], {}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'portal.rna': {
            'Meta': {'object_name': 'Rna', 'db_table': "'rna_myisam'"},
            'crc64': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'len': ('django.db.models.fields.IntegerField', [], {}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'seq_long': ('django.db.models.fields.TextField', [], {}),
            'seq_short': ('django.db.models.fields.CharField', [], {'max_length': '4000'}),
            'timestamp': ('django.db.models.fields.DateField', [], {}),
            'upi': ('django.db.models.fields.CharField', [], {'max_length': '13', 'primary_key': 'True'}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'portal.xref': {
            'Meta': {'object_name': 'Xref', 'db_table': "'xref_myisam'"},
            'ac': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accession'", 'db_column': "'ac'", 'to': u"orm['portal.Ac']"}),
            'created': ('django.db.models.fields.IntegerField', [], {}),
            'dbid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'release'", 'primary_key': True, 'db_column': "'id'", 'to': u"orm['portal.Release']"}),
            'deleted': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last': ('django.db.models.fields.IntegerField', [], {}),
            'taxid': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'upi': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'xrefs'", 'db_column': "'UPI'", 'to': u"orm['portal.Rna']"}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.IntegerField', [], {}),
            'version_i': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['portal']