# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_clusteringmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlastResult',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('query', models.CharField(max_length=13, db_index=True)),
                ('target', models.CharField(max_length=13, db_index=True)),
                ('identity', models.FloatField(db_index=True)),
                ('length', models.IntegerField()),
                ('mismatches', models.IntegerField()),
                ('gapopenings', models.IntegerField()),
                ('query_start', models.IntegerField()),
                ('query_end', models.IntegerField()),
                ('target_start', models.IntegerField()),
                ('target_end', models.IntegerField()),
                ('evalue', models.FloatField()),
                ('bitscore', models.FloatField()),
            ],
            options={
                'db_table': 'rnc_blast_results',
            },
            bases=(models.Model,),
        ),
    ]
