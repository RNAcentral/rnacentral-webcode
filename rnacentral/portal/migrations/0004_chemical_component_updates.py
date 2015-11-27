# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_modification'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalcomponent',
            name='ccd_id',
            field=models.CharField(default=b'', max_length=3),
        ),
        migrations.AlterField(
            model_name='chemicalcomponent',
            name='id',
            field=models.CharField(max_length=8, serialize=False, primary_key=True),
        ),
    ]
