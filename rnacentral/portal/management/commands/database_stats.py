"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.core.management.base import BaseCommand
from optparse import make_option
from portal.models import Database, Rna
from portal.models.database_stats import DatabaseStats
from portal.views import _get_json_lineage_tree
from django.db.models import Min, Max, Count, Avg
import json

import psycopg2
from portal.management.commands.common_exporters.database_connection import get_db_connection

####################
# Export functions #
####################

def get_lineages(dbid):
    """
    Construct a common taxonomic tree for all species annotated by an expert database.
    The tree is visualised on the expert database page.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """
    SELECT distinct classification, taxid
    from xref, rnc_accessions
    WHERE
        xref.ac = rnc_accessions.accession
        and xref.dbid = {dbid}
        and xref.deleted = 'N'
    """
    cursor.execute(sql.format(dbid=dbid))
    data = []
    for result in cursor:
        data.append((result['classification'], result['taxid']))
    return _get_json_lineage_tree(data)


def compute_database_stats(database):
    """
    Precompute database statistics for display on Expert Database landing pages.

    avg_length
    min_length
    max_length
    num_sequences
    num_organisms
    length_counts
    taxonomic_lineage
    """
    for expert_db in Database.objects.order_by('-id').all():
        if database:
            if expert_db.descr != database.upper():
                continue

        print expert_db.descr

        context = dict()
        rnas = Rna.objects.filter(xrefs__deleted='N',
                                  xrefs__db_id=expert_db.id)

        # avg_length, min_length, max_length, len_counts
        context.update(rnas.aggregate(min_length=Min('length'),
                                      max_length=Max('length'),
                                      avg_length=Avg('length')))
        context['len_counts'] = list(rnas.values('length').\
                                     annotate(counts=Count('length')).\
                                     order_by('length'))

        # update expert_db object
        expert_db.avg_length = context['avg_length']
        expert_db.min_length = context['min_length']
        expert_db.max_length = context['max_length']
        expert_db.num_sequences = expert_db.count_sequences()
        expert_db.num_organisms = expert_db.count_organisms()
        expert_db.save()

        expert_db_stats, created = DatabaseStats.objects.get_or_create(
            database=expert_db.descr,
            defaults={
                'length_counts': '',
                'taxonomic_lineage': ''
            })
        # django produces 'counts' keys, but d3 expects 'count' keys
        expert_db_stats.length_counts = json.dumps(context['len_counts']).\
                                  replace('counts', 'count')
        expert_db_stats.taxonomic_lineage = lineages
        expert_db_stats.taxonomic_lineage = get_lineages(expert_db.id)
        expert_db_stats.save()


class Command(BaseCommand):
    """
    Usage:
    python manage.py database_stats
    """

    ########################
    # Command line options #
    ########################

    option_list = BaseCommand.option_list + (
        make_option('-d',
            default='',
            dest='database',
            help='[Optional] Expert Database that needs to be recomputed'),
    )
    # shown with -h, --help
    help = ('Calculate per-database statistics used for Expert Database '
            'landing pages')

    def handle(self, *args, **options):
        """
        Django entry point
        """
        compute_database_stats(options['database'])
