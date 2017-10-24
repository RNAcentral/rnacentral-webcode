# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0012_auto_20170712_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='rnaprecomputed',
            name='rfam_problems',
            field=models.TextField(default=b''),
        ),
    ]
