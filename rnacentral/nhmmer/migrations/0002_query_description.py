# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nhmmer', '0001_squashed_0004_auto_20150409_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='description',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
