# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_chemical_component_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemicalcomponent',
            name='source',
            field=models.CharField(default=b'', max_length=10),
        ),
    ]
