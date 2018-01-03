# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0018_auto_20171214_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ensemblassembly',
            name='assembly_ucsc',
            field=models.CharField(max_length=100, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ensemblassembly',
            name='gca_accession',
            field=models.CharField(max_length=20, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ensemblassembly',
            name='taxid',
            field=models.IntegerField(unique=True, db_index=True),
        ),
    ]
