# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0006_auto_20141007_0947'),
    ]

    operations = [
        migrations.CreateModel(
            name='RnaPrecomputedData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=250, db_index=True)),
                ('count_human_xrefs', models.PositiveIntegerField(db_index=True)),
                ('count_distinct_organisms', models.PositiveIntegerField(db_index=True)),
                ('has_human_genomic_coordinates', models.NullBooleanField(db_index=True)),
                ('N_symbols', models.PositiveSmallIntegerField(db_index=True)),
                ('upi', models.ForeignKey(related_name=b'precomputed', db_column=b'upi', to='portal.Rna', unique=True)),
            ],
            options={
                'db_table': 'rnc_rna_precomputed_data',
            },
            bases=(models.Model,),
        ),
    ]
