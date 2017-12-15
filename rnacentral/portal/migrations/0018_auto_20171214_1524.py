# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0017_auto_20171214_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ensemblinsdcmapping',
            name='assembly_id',
            field=models.ForeignKey(related_name='assembly', db_column=b'assembly_id', to='portal.EnsemblAssembly'),
        ),
    ]
