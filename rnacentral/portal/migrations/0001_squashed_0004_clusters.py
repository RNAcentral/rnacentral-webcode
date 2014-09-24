# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'portal', '0001_initial'), (b'portal', '0002_clusters'), (b'portal', '0003_delete_clusters'), (b'portal', '0004_clusters')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('accession', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('parent_ac', models.CharField(max_length=100)),
                ('seq_version', models.IntegerField()),
                ('feature_start', models.IntegerField()),
                ('feature_end', models.IntegerField()),
                ('feature_name', models.CharField(max_length=20)),
                ('ordinal', models.IntegerField()),
                ('division', models.CharField(max_length=3)),
                ('keywords', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=250)),
                ('species', models.CharField(max_length=150)),
                ('organelle', models.CharField(max_length=100)),
                ('classification', models.CharField(max_length=500)),
                ('project', models.CharField(max_length=50)),
                ('is_composite', models.CharField(max_length=1)),
                ('non_coding_id', models.CharField(max_length=100)),
                ('database', models.CharField(max_length=20)),
                ('external_id', models.CharField(max_length=150)),
                ('optional_id', models.CharField(max_length=100)),
                ('anticodon', models.CharField(max_length=50)),
                ('experiment', models.CharField(max_length=500)),
                ('function', models.CharField(max_length=500)),
                ('gene', models.CharField(max_length=50)),
                ('gene_synonym', models.CharField(max_length=400)),
                ('inference', models.CharField(max_length=100)),
                ('locus_tag', models.CharField(max_length=50)),
                ('genome_position', models.CharField(max_length=200, db_column=b'map')),
                ('mol_type', models.CharField(max_length=50)),
                ('ncrna_class', models.CharField(max_length=50)),
                ('note', models.CharField(max_length=1500)),
                ('old_locus_tag', models.CharField(max_length=50)),
                ('product', models.CharField(max_length=300)),
                ('db_xref', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'rnc_accessions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('descr', models.CharField(max_length=30)),
                ('current_release', models.IntegerField()),
                ('full_descr', models.CharField(max_length=255)),
                ('alive', models.CharField(max_length=1)),
                ('for_release', models.CharField(max_length=1)),
                ('display_name', models.CharField(max_length=40)),
                ('project_id', models.CharField(max_length=10)),
                ('avg_length', models.IntegerField()),
                ('min_length', models.IntegerField()),
                ('max_length', models.IntegerField()),
                ('num_sequences', models.IntegerField()),
                ('num_organisms', models.IntegerField()),
            ],
            options={
                'db_table': 'rnc_database',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DatabaseStats',
            fields=[
                ('database', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('length_counts', models.TextField()),
                ('taxonomic_lineage', models.TextField()),
            ],
            options={
                'db_table': 'rnc_database_json_stats',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GenomicCoordinates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('primary_accession', models.CharField(max_length=50)),
                ('local_start', models.IntegerField()),
                ('local_end', models.IntegerField()),
                ('chromosome', models.CharField(max_length=50, db_column=b'name')),
                ('primary_start', models.IntegerField()),
                ('primary_end', models.IntegerField()),
                ('strand', models.IntegerField()),
                ('accession', models.ForeignKey(related_name=b'coordinates', db_column=b'accession', to='portal.Accession')),
            ],
            options={
                'db_table': 'rnc_coordinates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('authors', models.TextField()),
                ('location', models.CharField(max_length=4000)),
                ('title', models.CharField(max_length=4000)),
                ('pubmed', models.CharField(max_length=10, db_column=b'pmid')),
                ('doi', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'rnc_references',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reference_map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accession', models.ForeignKey(related_name=b'refs', db_column=b'accession', to='portal.Accession')),
                ('data', models.ForeignKey(to='portal.Reference', db_column=b'reference_id')),
            ],
            options={
                'db_table': 'rnc_reference_map',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('release_date', models.DateField()),
                ('release_type', models.CharField(max_length=1)),
                ('status', models.CharField(max_length=1)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('descr', models.TextField()),
                ('force_load', models.CharField(max_length=1)),
                ('db', models.ForeignKey(related_name=b'db', db_column=b'dbid', to='portal.Database')),
            ],
            options={
                'db_table': 'rnc_release',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rna',
            fields=[
                ('id', models.IntegerField(db_column=b'id')),
                ('upi', models.CharField(max_length=13, serialize=False, primary_key=True, db_index=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('crc64', models.CharField(max_length=16)),
                ('length', models.IntegerField(db_column=b'len')),
                ('seq_short', models.CharField(max_length=4000)),
                ('seq_long', models.TextField()),
                ('md5', models.CharField(unique=True, max_length=32, db_index=True)),
            ],
            options={
                'db_table': 'rna',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Xref',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version_i', models.IntegerField()),
                ('deleted', models.CharField(max_length=1)),
                ('timestamp', models.DateTimeField()),
                ('userstamp', models.CharField(max_length=100)),
                ('version', models.IntegerField()),
                ('taxid', models.IntegerField()),
                ('accession', models.ForeignKey(related_name=b'xrefs', db_column=b'ac', to='portal.Accession', unique=True)),
                ('created', models.ForeignKey(related_name=b'release_created', db_column=b'created', to='portal.Release')),
                ('db', models.ForeignKey(related_name=b'xrefs', db_column=b'dbid', to='portal.Database')),
                ('last', models.ForeignKey(related_name=b'last_release', db_column=b'last', to='portal.Release')),
                ('upi', models.ForeignKey(related_name=b'xrefs', db_column=b'upi', to='portal.Rna')),
            ],
            options={
                'db_table': 'xref',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('cluster_id', models.CharField(max_length=200, db_index=True)),
                ('size', models.IntegerField(db_index=True)),
                ('method_id', models.IntegerField()),
            ],
            options={
                'db_table': 'rnc_clusters',
            },
            bases=(models.Model,),
        ),
    ]
