# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('query', models.TextField()),
                ('length', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'nhmmer_query',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('query_id', models.CharField(max_length=36, db_index=True)),
                ('result_id', models.PositiveIntegerField(db_index=True)),
                ('alignment', models.TextField(null=True)),
                ('e_value', models.FloatField(null=True)),
                ('score', models.FloatField(null=True)),
                ('bias', models.FloatField(null=True)),
                ('description', models.TextField(null=True)),
                ('query_end', models.PositiveIntegerField(null=True)),
                ('query_start', models.PositiveIntegerField(null=True)),
                ('rnacentral_id', models.CharField(max_length=13, null=True)),
                ('target_end', models.PositiveIntegerField(null=True)),
                ('target_length', models.PositiveIntegerField(null=True)),
                ('target_start', models.PositiveIntegerField(null=True)),
            ],
            options={
                'db_table': 'nhmmer_results',
            },
            bases=(models.Model,),
        ),
    ]
