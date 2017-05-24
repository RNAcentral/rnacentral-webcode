#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import codecs
import collections as coll

import click
import django

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))
django.setup()

from portal.models import RfamClan
from portal.models import RfamModel
from portal.models import RfamHit
from portal.models import RfamSearch
from portal.models import SequenceRegion
from portal.models import RfamModelRegion
from portal.utils import rfam as rfutil


def sequence_region(data):
    data = {
        'upi_id': data['urs'],
        'start': int(data['seq_from']) - 1,
        'stop': int(data['seq_to']),
    }
    query = SequenceRegion.objects.filter(**data)
    if query:
        return query.get()
    return SequenceRegion.objects.create(completeness=0, **data)


def model_region(data):
    data = {
        'rfam_model_id_id': data['rfam_acc'],
        'start': int(data['mdl_from']) - 1,
        'stop': int(data['mdl_to']),
    }
    query = RfamModelRegion.objects.filter(**data)
    if query:
        return query.get()
    return RfamModelRegion.objects.create(completeness=0, **data)


@click.group()
def main():
    pass


@main.command('metadata')
@click.option('--version', default='CURRENT')
def metadata(version=None):
    mapping = coll.defaultdict(set)
    for (clan, rfam) in rfutil.get_clan_membership(version=version):
        mapping[clan].add(rfam)
        mapping[rfam].add(clan)

    clans = {}
    for clan in rfutil.get_clans(version=version):
        description = clan[5]
        clan_model = RfamClan(
            rfam_clan_id=clan[0],
            name=clan[1],
            description=description,
            family_count=len(mapping[clan[0]]),
        )
        clans[clan[0]] = clan_model
        clan_model.save()

    for family in rfutil.get_families(version=version):
        assigned = mapping.get(family[0], None)
        clan = None
        if assigned:
            clan = clans[assigned.pop()]

        rfam = RfamModel(
            rfam_model_id=family[0],
            name=family[1],
            description=family[9].replace(chr(0xfc), ''),
            rfam_clan_id=clan,
            seed_count=int(family[14]),
            full_count=int(family[15]),
            length=int(family[28]),
        )
        rfam.save()


def search():
    data = {
        'rfam_release_version': '12.0',
        'program': 'cmscan',
        'program_version': '',
        'program_options': '',
    }
    query = RfamSearch.objects.filter(**data)
    if query:
        return query.get()
    return RfamSearch.objects.create(**data)


@main.command('hits')
@click.argument('filename', type=click.Path(readable=True))
def hits(filename):
    with open(filename, 'rb') as raw:
        for row in csv.DictReader(raw, delimiter='\t'):
            hit = RfamHit()
            hit.rfam_search_id = search().rfam_search_id
            hit.sequence_region = sequence_region(row)
            hit.rfam_model_region = model_region(row)
            hit.e_value = float(row['e_value'])
            hit.score = float(row['score'])
            hit.save()


if __name__ == '__main__':
    main()
