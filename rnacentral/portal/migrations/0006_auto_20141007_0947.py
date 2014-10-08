# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_blastresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accession',
            name='feature_end',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='accession',
            name='feature_start',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='accession',
            name='seq_version',
            field=models.IntegerField(db_index=True),
        ),
    ]
