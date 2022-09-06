# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0007_add_precomputed_rna_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rnaprecomputed",
            name="taxid",
            field=models.IntegerField(null=True, db_index=True),
        ),
    ]
