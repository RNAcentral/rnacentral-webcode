# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0012_auto_201706008_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfammodel',
            name='domain',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
