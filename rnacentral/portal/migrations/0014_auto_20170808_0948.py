# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0013_auto_20170803_1056'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoTerm',
            fields=[
                ('go_term_id', models.CharField(max_length=10, serialize=False, primary_key=True, db_index=True)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'go_terms',
            },
        ),
        migrations.CreateModel(
            name='RfamGoTerm',
            fields=[
                ('rfam_go_term_id', models.AutoField(serialize=False, primary_key=True)),
                ('go_term', models.ForeignKey(to='portal.GoTerm', db_column=b'go_term_id')),
                ('rfam_model', models.ForeignKey(to='portal.RfamModel', db_column=b'rfam_model_id')),
            ],
            options={
                'db_table': 'rfam_go_terms',
            },
        ),
        migrations.AlterUniqueTogether(
            name='rfamgoterm',
            unique_together=set([('rfam_model', 'go_term')]),
        ),
    ]
