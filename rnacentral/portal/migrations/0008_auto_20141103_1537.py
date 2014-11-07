# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_rnaprecomputeddata'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditDistance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('query', models.CharField(max_length=13, db_index=True)),
                ('target', models.CharField(max_length=13, db_index=True)),
                ('distance', models.IntegerField()),
            ],
            options={
                'db_table': 'rnc_edit_distance',
            },
            bases=(models.Model,),
        ),
    ]
