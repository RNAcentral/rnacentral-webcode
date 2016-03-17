# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0006_add_modomics_short_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='RnaPrecomputed',
            fields=[
                ('id', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('taxid', models.IntegerField(db_index=True)),
                ('description', models.CharField(max_length=250)),
                ('upi', models.ForeignKey(related_name='precomputed', db_column=b'upi', to='portal.Rna')),
            ],
            options={
                'db_table': 'rnc_rna_precomputed',
            },
        ),
    ]
