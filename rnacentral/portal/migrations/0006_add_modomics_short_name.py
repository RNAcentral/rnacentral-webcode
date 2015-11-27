# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_add_source_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalcomponent',
            name='modomics_short_name',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
