# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0008_auto_20160311_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rnaprecomputed',
            name='id',
            field=models.CharField(max_length=22, serialize=False, primary_key=True),
        ),
    ]
