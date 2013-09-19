# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Rna'
        db.create_table('rna_myisam', (
            ('upi', self.gf('django.db.models.fields.CharField')(max_length=13, primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateField')()),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('crc64', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('len', self.gf('django.db.models.fields.IntegerField')()),
            ('seq_short', self.gf('django.db.models.fields.CharField')(max_length=4000)),
            ('seq_long', self.gf('django.db.models.fields.TextField')()),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'portal', ['Rna'])

        # Adding model 'Database'
        db.create_table('rnc_database', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateField')()),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('descr', self.gf('django.db.models.fields.TextField')()),
            ('current_release', self.gf('django.db.models.fields.IntegerField')()),
            ('full_descr', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('alive', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('for_release', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'portal', ['Database'])

        # Adding model 'Release'
        db.create_table('rnc_release', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('db', self.gf('django.db.models.fields.related.ForeignKey')(related_name='db', db_column='db_id', to=orm['portal.Database'])),
            ('release_date', self.gf('django.db.models.fields.DateField')()),
            ('release_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.DateField')()),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('descr', self.gf('django.db.models.fields.TextField')()),
            ('force_load', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'portal', ['Release'])

        # Adding model 'Ac'
        db.create_table('rnc_ac_info', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True, db_column='ac')),
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

        # Adding model 'Xref'
        db.create_table('xref_myisam', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('db', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Database'], db_column='db_id')),
            ('created', self.gf('django.db.models.fields.related.ForeignKey')(related_name='release_created', db_column='created', to=orm['portal.Release'])),
            ('last', self.gf('django.db.models.fields.related.ForeignKey')(related_name='last_release', db_column='last', to=orm['portal.Release'])),
            ('upi', self.gf('django.db.models.fields.related.ForeignKey')(related_name='xrefs', db_column='UPI', to=orm['portal.Rna'])),
            ('version_i', self.gf('django.db.models.fields.IntegerField')()),
            ('deleted', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('userstamp', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Ac'], null=True, db_column='ac', blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('taxid', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'portal', ['Xref'])

        # Adding model 'CompositeId'
        db.create_table('rnc_composite_ids', (
            ('composite_id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('ac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Ac'])),
            ('database', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('optional_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'portal', ['CompositeId'])


    def backwards(self, orm):
        # Deleting model 'Rna'
        db.delete_table('rna_myisam')

        # Deleting model 'Database'
        db.delete_table('rnc_database')

        # Deleting model 'Release'
        db.delete_table('rnc_release')

        # Deleting model 'Ac'
        db.delete_table('rnc_ac_info')

        # Deleting model 'Xref'
        db.delete_table('xref_myisam')

        # Deleting model 'CompositeId'
        db.delete_table('rnc_composite_ids')


    models = {
        u'portal.ac': {
            'Meta': {'object_name': 'Ac', 'db_table': "'rnc_ac_info'"},
            'classification': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'division': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'feature_end': ('django.db.models.fields.IntegerField', [], {}),
            'feature_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'feature_start': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_column': "'ac'"}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ordinal': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'organelle': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent_ac': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'seq_version': ('django.db.models.fields.IntegerField', [], {}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'portal.compositeid': {
            'Meta': {'object_name': 'CompositeId', 'db_table': "'rnc_composite_ids'"},
            'ac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portal.Ac']"}),
            'composite_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'database': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'optional_id': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'db': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'db'", 'db_column': "'db_id'", 'to': u"orm['portal.Database']"}),
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
            'accession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portal.Ac']", 'null': 'True', 'db_column': "'ac'", 'blank': 'True'}),
            'created': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'release_created'", 'db_column': "'created'", 'to': u"orm['portal.Release']"}),
            'db': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portal.Database']", 'db_column': "'db_id'"}),
            'deleted': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_release'", 'db_column': "'last'", 'to': u"orm['portal.Release']"}),
            'taxid': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'upi': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'xrefs'", 'db_column': "'UPI'", 'to': u"orm['portal.Rna']"}),
            'userstamp': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.IntegerField', [], {}),
            'version_i': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['portal']