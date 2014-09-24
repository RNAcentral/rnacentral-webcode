# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_clustermember'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusteringMethod',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('command', models.TextField()),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'rnc_clustering_method',
            },
            bases=(models.Model,),
        ),
    ]
