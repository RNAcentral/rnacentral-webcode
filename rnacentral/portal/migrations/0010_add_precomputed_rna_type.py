from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_add_precomputed_rna_table'),
    ]

    operations = [
        # rna_type is a / seperated field that represents the set of rna_types
        # for a given sequence.
        migrations.AddField("RnaPrecomputed", "rna_type", models.CharField(max_length=250))
    ]
