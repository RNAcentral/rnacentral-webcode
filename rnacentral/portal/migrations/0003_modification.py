# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import caching.base
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0002_chemicalcomponent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Modification",
            fields=[
                ("id", models.AutoField(serialize=False, primary_key=True)),
                ("position", models.PositiveIntegerField()),
                ("author_assigned_position", models.IntegerField()),
                (
                    "modification_id",
                    models.ForeignKey(
                        to="portal.ChemicalComponent",
                        db_column=b"modification_id",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "upi",
                    models.ForeignKey(
                        related_name="modifications",
                        db_column=b"upi",
                        to="portal.Rna",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "xref",
                    models.ForeignKey(
                        related_name="modifications",
                        db_column=b"accession",
                        to_field=b"accession",
                        to="portal.Xref",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "db_table": "rnc_modifications",
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
    ]
