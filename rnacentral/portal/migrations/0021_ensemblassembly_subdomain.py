# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-08 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0020_auto_20180405_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='ensemblassembly',
            name='subdomain',
            field=models.CharField(db_index=True, default=b'ensembl.org', max_length=100),
        ),
    ]
