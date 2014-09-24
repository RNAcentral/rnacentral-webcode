# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_squashed_0004_clusters'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusters',
            name='chromosome',
            field=models.CharField(max_length=50, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clusters',
            name='end',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clusters',
            name='start',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
