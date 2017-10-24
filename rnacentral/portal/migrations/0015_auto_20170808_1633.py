# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0014_auto_20170808_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfammodel',
            name='rfam_rna_type',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
