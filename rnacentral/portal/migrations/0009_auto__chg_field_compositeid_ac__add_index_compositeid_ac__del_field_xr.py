# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'CompositeId.ac' to match new field type.
        db.rename_column('rnc_composite_ids', 'ac', 'ac_id')
        # Changing field 'CompositeId.ac'
        db.alter_column('rnc_composite_ids', 'ac_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Ac']))
        # Adding index on 'CompositeId', fields ['ac']
        db.create_index('rnc_composite_ids', ['ac_id'])

        # Deleting field 'Xref.ac'
        db.delete_column('xref_myisam', 'ac')

        # Deleting field 'Xref.dbid'
        db.delete_column('xref_myisam', 'id')

        # Adding field 'Xref.db'
        db.add_column('xref_myisam', 'db',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['portal.Database'], db_column='db_id'),
                      keep_default=False)

        # Adding field 'Xref.accession'
        db.add_column('xref_myisam', 'accession',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Ac'], null=True, db_column='ac', blank=True),
                      keep_default=False)


        # Changing field 'Xref.last'
        db.alter_column('xref_myisam', 'last', self.gf('django.db.models.fields.related.ForeignKey')(db_column='last', to=orm['portal.Release']))
        # Adding index on 'Xref', fields ['last']
        db.create_index('xref_myisam', ['last'])


        # Changing field 'Xref.created'
        db.alter_column('xref_myisam', 'created', self.gf('django.db.models.fields.related.ForeignKey')(db_column='created', to=orm['portal.Release']))
        # Adding index on 'Xref', fields ['created']
        db.create_index('xref_myisam', ['created'])

        # Deleting field 'Ac.ac'
        db.delete_column('rnc_ac_info', 'ac')

        # Adding field 'Ac.id'
        db.add_column('rnc_ac_info', 'id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, primary_key=True, db_column='ac'),
                      keep_default=False)


        # Changing field 'Release.db'
        db.alter_column('rnc_release', 'db_id', self.gf('django.db.models.fields.related.ForeignKey')(db_column='db_id', to=orm['portal.Database']))

    def backwards(self, orm):
        # Removing index on 'Xref', fields ['created']
        db.delete_index('xref_myisam', ['created'])

        # Removing index on 'Xref', fields ['last']
        db.delete_index('xref_myisam', ['last'])

        # Removing index on 'CompositeId', fields ['ac']
        db.delete_index('rnc_composite_ids', ['ac_id'])


        # Renaming column for 'CompositeId.ac' to match new field type.
        db.rename_column('rnc_composite_ids', 'ac_id', 'ac')
        # Changing field 'CompositeId.ac'
        db.alter_column('rnc_composite_ids', 'ac', self.gf('django.db.models.fields.CharField')(max_length=100))
        # Adding field 'Xref.ac'
        db.add_column('xref_myisam', 'ac',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='accession', db_column='ac', to=orm['portal.Ac']),
                      keep_default=False)

        # Adding field 'Xref.dbid'
        db.add_column('xref_myisam', 'dbid',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='release', primary_key=True, db_column='id', to=orm['portal.Release']),
                      keep_default=False)

        # Deleting field 'Xref.db'
        db.delete_column('xref_myisam', 'db_id')

        # Deleting field 'Xref.accession'
        db.delete_column('xref_myisam', 'ac')


        # Changing field 'Xref.last'
        db.alter_column('xref_myisam', 'last', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Xref.created'
        db.alter_column('xref_myisam', 'created', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'Ac.ac'
        db.add_column('rnc_ac_info', 'ac',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, primary_key=True),
                      keep_default=False)

        # Deleting field 'Ac.id'
        db.delete_column('rnc_ac_info', 'ac')


        # Changing field 'Release.db'
        db.alter_column('rnc_release', 'db_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Database']))

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