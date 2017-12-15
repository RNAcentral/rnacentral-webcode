# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import caching.base


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0016_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnsemblAssembly',
            fields=[
                ('assembly_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('assembly_full_name', models.CharField(max_length=255, db_index=True)),
                ('gca_accession', models.CharField(max_length=20, db_index=True)),
                ('assembly_ucsc', models.CharField(max_length=100, db_index=True)),
                ('common_name', models.CharField(max_length=255, db_index=True)),
                ('taxid', models.IntegerField(db_index=True)),
            ],
            options={
                'db_table': 'ensembl_assembly',
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EnsemblInsdcMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insdc', models.CharField(max_length=255, db_index=True)),
                ('ensembl_name', models.CharField(max_length=255, db_index=True)),
                ('assembly_id', models.ForeignKey(related_name='assembly', to='portal.EnsemblAssembly')),
            ],
            options={
                'db_table': 'ensembl_insdc_mapping',
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
    ]
