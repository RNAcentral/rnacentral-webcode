from __future__ import unicode_literals

import caching.base
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0020_auto_20180216_0931')
    ]

    operations = [
        migrations.CreateModel(
            name='GenomeMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chromosome', models.CharField(max_length=100)),
                ('region_id', models.CharField(max_length=100)),
                ('rna_id', models.CharField(max_length=50)),
                ('start', models.IntegerField()),
                ('stop', models.IntegerField()),
                ('strand', models.CharField(choices=[(b'+', b'forward'), (b'-', b'reverse')], max_length=10)),
                ('taxid', models.IntegerField()),
                ('assembly_id', models.ForeignKey(db_column=b'assembly_id', on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='genome_mappings', to='portal.EnsemblAssembly')),
                ('upi', models.ForeignKey(db_column=b'upi', on_delete=django.db.models.deletion.CASCADE,
                                          related_name='genome_mappings', to='portal.Rna')),
            ],
            options={
                'db_table': 'load_genome_mapping',
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
    ]
