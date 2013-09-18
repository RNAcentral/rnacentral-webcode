# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ac'
        db.create_table('rnc_ac_info', (
            ('ac', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('parent_ac', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('seq_version', self.gf('django.db.models.fields.IntegerField')()),
            ('feature_start', self.gf('django.db.models.fields.IntegerField')()),
            ('feature_end', self.gf('django.db.models.fields.IntegerField')()),
            ('feature_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('ordinal', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('division', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('species', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('organelle', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('classification', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('project', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'portal', ['Ac'])

        # Changing field 'Rna.upi'
        db.alter_column('rna_myisam', 'upi', self.gf('django.db.models.fields.CharField')(max_length=13, primary_key=True))
        # Adding unique constraint on 'Rna', fields ['upi']
        db.create_unique('rna_myisam', ['upi'])


        # Changing field 'Rna.timestamp'
        db.alter_column('rna_myisam', 'timestamp', self.gf('django.db.models.fields.DateField')())

        # Changing field 'Rna.userstamp'
        db.alter_column('rna_myisam', 'userstamp', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'Xref.ac'
        db.alter_column('xref_myisam', 'ac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Ac'], db_column='ac'))
        # Adding index on 'Xref', fields ['ac']
        db.create_index('xref_myisam', ['ac'])


        # Renaming column for 'Xref.upi' to match new field type.
        db.rename_column('xref_myisam', 'upi_id', 'UPI')
        # Changing field 'Xref.upi'
        db.alter_column('xref_myisam', 'UPI', self.gf('django.db.models.fields.related.ForeignKey')(db_column='UPI', to=orm['portal.Rna']))

        # Changing field 'Xref.id'
        db.alter_column('xref_myisam', 'id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))

    def backwards(self, orm):
        # Removing index on 'Xref', fields ['ac']
        db.delete_index('xref_myisam', ['ac'])

        # Removing unique constraint on 'Rna', fields ['upi']
        db.delete_unique('rna_myisam', ['upi'])

        # Deleting model 'Ac'
        db.delete_table('rnc_ac_info')


        # Changing field 'Rna.upi'
        db.alter_column('rna_myisam', 'upi', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'Rna.timestamp'
        db.alter_column('rna_myisam', 'timestamp', self.gf('django.db.models.fields.CharField')(max_length=10))

        # Changing field 'Rna.userstamp'
        db.alter_column('rna_myisam', 'userstamp', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Xref.ac'
        db.alter_column('xref_myisam', 'ac', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Renaming column for 'Xref.upi' to match new field type.
        db.rename_column('xref_myisam', 'UPI', 'upi_id')
        # Changing field 'Xref.upi'
        db.alter_column('xref_myisam', 'upi_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Rna']))

        # Changing field 'Xref.id'
        db.alter_column('xref_myisam', u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

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
            'ac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portal.Ac']", 'db_column': "'ac'"}),
            'created': ('django.db.models.fields.IntegerField', [], {}),
            'dbid': ('django.db.models.fields.IntegerField', [], {}),
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