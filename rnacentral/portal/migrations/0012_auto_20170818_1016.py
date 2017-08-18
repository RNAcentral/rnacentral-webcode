# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0011_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecondaryStructure',
            fields=[
                ('ss_id', models.AutoField(serialize=False, primary_key=True)),
                ('secondary_structure', models.TextField()),
                ('md5', models.CharField(max_length=32, db_index=True)),
            ],
            options={
                'db_table': 'rnc_secondary_structure',
            },
        ),
        migrations.AddField(
            model_name='secondarystructure',
            name='accession',
            field=models.ForeignKey(related_name='secondary_structure', db_column=b'rnc_accession_id', to='portal.Accession'),
        ),
    ]
