# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import caching.base


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChemicalComponent',
            fields=[
                ('id', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=500)),
                ('one_letter_code', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'rnc_chemical_components',
            },
            bases=(models.Model,),
        ),
    ]
