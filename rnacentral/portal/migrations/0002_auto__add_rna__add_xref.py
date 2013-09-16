# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Rna'
        db.create_table('rna', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('upi', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('crc64', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('len', self.gf('django.db.models.fields.IntegerField')()),
            ('seq_short', self.gf('django.db.models.fields.CharField')(max_length=4000)),
            ('seq_long', self.gf('django.db.models.fields.TextField')()),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'portal', ['Rna'])

        # Adding model 'Xref'
        db.create_table('xref', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dbid', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.IntegerField')()),
            ('last', self.gf('django.db.models.fields.IntegerField')()),
            ('upi', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Rna'])),
            ('version_i', self.gf('django.db.models.fields.IntegerField')()),
            ('deleted', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ac', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('taxid', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'portal', ['Xref'])


    def backwards(self, orm):
        # Deleting model 'Rna'
        db.delete_table('rna')

        # Deleting model 'Xref'
        db.delete_table('xref')


    models = {
        u'portal.rna': {
            'Meta': {'object_name': 'Rna', 'db_table': "'rna'"},
            'crc64': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'len': ('django.db.models.fields.IntegerField', [], {}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'seq_long': ('django.db.models.fields.TextField', [], {}),
            'seq_short': ('django.db.models.fields.CharField', [], {'max_length': '4000'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'upi': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'portal.xref': {
            'Meta': {'object_name': 'Xref', 'db_table': "'xref'"},
            'ac': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'created': ('django.db.models.fields.IntegerField', [], {}),
            'dbid': ('django.db.models.fields.IntegerField', [], {}),
            'deleted': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last': ('django.db.models.fields.IntegerField', [], {}),
            'taxid': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'upi': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portal.Rna']"}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.IntegerField', [], {}),
            'version_i': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['portal']