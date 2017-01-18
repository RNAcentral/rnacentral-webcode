from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_add_precomputed_rna_table'),
    ]

    operations = [
        migrations.AddField("RnaPrecomputed", "rna_type", models.CharField(max_length=250))
    ]
