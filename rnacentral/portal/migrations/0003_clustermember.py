# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_auto_20140924_1302'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterMember',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('cluster_id', models.CharField(max_length=200, db_index=True)),
                ('upi', models.CharField(max_length=13, db_index=True)),
                ('method_id', models.IntegerField()),
            ],
            options={
                'db_table': 'rnc_cluster_members',
            },
            bases=(models.Model,),
        ),
    ]
