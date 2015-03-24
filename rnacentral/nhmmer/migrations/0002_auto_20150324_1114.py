# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nhmmer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='query_id',
            field=models.ForeignKey(related_name='results', db_column=b'query_id', to='nhmmer.Query'),
            preserve_default=True,
        ),
    ]
