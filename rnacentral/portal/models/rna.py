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

import operator as op
import itertools as it
from collections import Counter

from caching.base import CachingMixin, CachingManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Prefetch, Min, Max
from django.utils.functional import cached_property

from database import Database
from genomic_coordinates import GenomicCoordinates
from modification import Modification
from rna_precomputed import RnaPrecomputed
from reference import Reference
from xref import Xref
from .rfam import RfamHit, RfamAnalyzedSequences
from .accession import Accession

from formatters import Gff3Formatter, GffFormatter, _xref_to_bed_format
from portal.utils import descriptions as desc
from portal.rfam_matches import check_issues


class Rna(CachingMixin, models.Model):
    id = models.IntegerField(db_column='id')
    upi = models.CharField(max_length=13, db_index=True, primary_key=True)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    crc64 = models.CharField(max_length=16)
    length = models.IntegerField(db_column='len')
    seq_short = models.CharField(max_length=4000)
    seq_long = models.TextField()
    md5 = models.CharField(max_length=32, unique=True, db_index=True)

    objects = CachingManager()

    class Meta:
        db_table = 'rna'

    def get_absolute_url(self):
        """Get a URL for an RNA object. Used for generating sitemaps."""
        return reverse('unique-rna-sequence', kwargs={'upi': self.upi})

    def get_publications(self, taxid=None):
        """
        Get all publications associated with a Unique RNA Sequence.
        Use raw SQL query for better performance.
        """
        query = """
        SELECT b.id, b.location, b.title, b.pmid as pubmed, b.doi, b.authors
        FROM
            (SELECT DISTINCT t3.id
            FROM xref t1, rnc_reference_map t2, RNC_REFERENCES t3
            WHERE t1.ac = t2.accession AND
                  t1.upi = %s AND
                  {taxid_clause}
                  t2.reference_id = t3.id) a
        JOIN
            rnc_references b
        ON a.id = b.id
        ORDER BY b.title
        """

        query = query.format(taxid_clause='t1.taxid = %s AND' % taxid) if taxid else query.format(taxid_clause='')

        return Reference.objects.raw(query, [self.upi])

    def is_active(self):
        """A sequence is considered active if it has at least one active cross_reference."""
        values_list = self.xrefs.values_list('deleted', flat=True)
        print "self.xrefs.values_list('deleted', flat=True) = %s" % values_list
        return 'N' in self.xrefs.values_list('deleted', flat=True).distinct()  # deleted xrefs are marked with N

    def has_genomic_coordinates(self, taxid=None):
        """Return True if at least one cross-reference has genomic coordinates."""
        xrefs = self.xrefs
        if taxid:
            xrefs = xrefs.filter(taxid=taxid)
        chromosomes = xrefs.all().values_list('accession__coordinates__chromosome', flat=True)
        for chromosome in chromosomes:
            if chromosome:
                return True
        return False

    def get_sequence(self):
        """
        Sequences of up to 4000 nucleotides are stored in seq_short, while the
        longer ones are in stored in seq_long as CLOB objects
        due to Oracle column size restrictions.
        """
        if self.seq_short:
            sequence = self.seq_short
        else:
            sequence = self.seq_long
        return sequence.replace('T', 'U').upper()

    def count_symbols(self):
        """
        Returns the number of occurrences of all symbols in RNA,
        including non-canonical nucleotides and random garbage.
        :return: dict {'A': 1, 'T': 2, 'C': 3, 'G': 4, 'N': 5, 'I': 6, '*': 7}
        """
        return dict(Counter(self.get_sequence()))

    def get_xrefs(self, taxid=None):
        """
        Get all xrefs, show non-ENA annotations first.
        Exclude source ENA entries that are associated with other expert db entries.
        For example, only fetch Vega xrefs and don't retrieve the ENA entries they are
        based on.
        """
        expert_db_projects = Database.objects.exclude(project_id=None)\
                                             .values_list('project_id', flat=True)

        xrefs = self.xrefs.filter(deleted='N', upi=self.upi)\
                          .exclude(db__id=1, accession__project__in=expert_db_projects)\
                          .order_by('-db__id')\
                          .select_related()\
                          .prefetch_related(
                              Prefetch(
                                  'modifications',
                                  queryset=Modification.objects.select_related('modification_id')
                              )
                          )\
                          .prefetch_related(
                              Prefetch(
                                  'accession__coordinates',
                                  queryset=GenomicCoordinates.objects.filter(chromosome__isnull=False)
                              )
                          )\
                          .all()

        if taxid:
            xrefs = xrefs.for_taxid(taxid)

        return xrefs if xrefs.exists() else self.xrefs.filter(deleted='Y').select_related()

    def count_xrefs(self, taxid=None):
        """Count the number of cross-references associated with the sequence."""
        xrefs = self.xrefs.filter(db__project_id__isnull=True, deleted='N')
        if taxid:
            xrefs = xrefs.filter(taxid=taxid)
        return xrefs.count()

    @cached_property
    def count_distinct_organisms(self):
        """Count the number of distinct taxids referenced by the sequence."""
        queryset = self.xrefs.values('accession__species')
        results = queryset.filter(deleted='N').distinct().count()
        if not results:
            results = queryset.distinct().count()
        return results

    def get_distinct_database_names(self, taxid=None):
        """Get a non-redundant list of databases referencing the sequence."""
        databases = self.xrefs.filter(deleted='N')
        if taxid:
            databases = databases.filter(taxid=taxid)
        databases = list(databases.values_list('db__display_name', flat=True).distinct())
        databases = sorted(databases, key=lambda s: s.lower())  # case-insensitive
        return databases

    @cached_property
    def first_seen(self):
        """Return the earliest release the sequence is referenced in."""
        data = self.xrefs.aggregate(first_seen=Min('created__release_date'))
        return data['first_seen']

    @cached_property
    def last_seen(self):
        """Like `first_seen` but with reversed order."""
        data = self.xrefs.aggregate(last_seen=Max('last__release_date'))
        return data['last_seen']

    def get_sequence_fasta(self):
        """Split long sequences by a fixed number of characters per line."""
        max_column = 80
        seq = self.get_sequence()
        split_seq = ''
        i = 0
        while i < len(seq):
            split_seq += seq[i:i+max_column] + "\n"
            i += max_column
        description = self.get_description()
        fasta = ">%s %s\n%s" % (self.upi, description, split_seq)
        return fasta

    def get_gff(self):
        """
        Format genomic coordinates from all xrefs into a single file in GFF2 format.
        To reduce redundancy, keep only xrefs from the source entries,
        not the entries added from the DR lines.
        """
        xrefs = self.xrefs.filter(db__project_id__isnull=True).all()
        gff = ''
        for xref in xrefs:
            gff += GffFormatter(xref)()
        return gff

    def get_gff3(self):
        """Format genomic coordinates from all xrefs into a single file in GFF3 format."""
        xrefs = self.xrefs.filter(deleted='N').all()
        gff = '##gff-version 3\n'
        for xref in xrefs:
            gff += Gff3Formatter(xref)()
        return gff

    def get_ucsc_bed(self):
        """
        Format genomic coordinates from all xrefs into a single file in UCSC BED format.
        Example:
        chr1    29554    31097    RNA000063C361    0    +   29554    31097    255,0,0    3    486,104,122    0,1009,1421
        """
        xrefs = self.xrefs.filter(db__project_id__isnull=True).all()
        bed = ''
        for xref in xrefs:
            bed += _xref_to_bed_format(xref)
        return bed

    def get_rna_type(self, taxid=None, recompute=False):
        """Determine the rna type for the given sequence. This will use the
        precomuted data if possible. If not asked to recompute it will do so.
        Providing an taxid will compute the rna_type for the given taxon only.
        This means it will determine the rna_type for only that organism.

        Parameters
        ----------
        taxid : int, None
            The taxon id, if any to use for finding the rna_type.
        recompute : bool, False
            Flag to indicate if this should use the already stored data, or
            recompute it.

        Returns
        -------
        rna_type : str
            The rna type computed for this sequence and possibly taxon id.
        """

        if not recompute:
            queryset = RnaPrecomputed.objects.filter(taxid=taxid)
            try:
                rna_type = queryset.get(upi=self.upi).rna_type
                if rna_type is None:
                    xrefs = self.find_valid_xrefs(taxid=taxid)
                    return desc.get_rna_type(self, xrefs, taxid=taxid)
                return rna_type
            except ObjectDoesNotExist:
                pass

        xrefs = self.find_valid_xrefs(taxid=taxid)
        return desc.get_rna_type(self, xrefs, taxid=taxid)

    def get_description(self, taxid=None, recompute=False):
        """
        Compute the description of this sequence. The description is intented
        to be a good description of the sequence and is based upon the xrefs
        this sequence has. If given a taxid this will produce a description
        that is specific to that species, otherwise it will return a
        description that is general for all species this has been observed in.

        Normally, this will simply lookup a stored description in
        rna_precomputed, however, if recompute=True is given then this will
        recompute the description.


        Parameters
        ----------
        taxid : int, None
            The taxon id to create a description for.

        recompute : bool, False
            If this should compute the description or simply look it up.

        Returns
        -------
        description : str
            The description of this sequence.
        """
        if not recompute:
            if taxid:
                queryset = RnaPrecomputed.objects.filter(taxid=taxid)
            else:
                queryset = RnaPrecomputed.objects.filter(taxid__isnull=True)

            try:
                obj = queryset.get(upi=self.upi)
                return obj.description
            except ObjectDoesNotExist:
                pass

        xrefs = self.find_valid_xrefs(taxid=taxid)
        return desc.get_description(self, xrefs, taxid=taxid)

    def find_valid_xrefs(self, taxid=None):
        """
        Determine the valid xrefs for this sequence and taxid. This will
        attempt to get all active (not deleted) xrefs for the given sequence
        and taxon id. If there are no active xrefs then this will switch to use
        the deleted xrefs.

        taxid : int, None
            The taxon id to use. None indicates no species constraint,
            otherwise the taxid is the taxid of the xref to limit to.

        Returns
        -------
        xrefs : queryset
            The collection of xrefs that are valid for the sequence and taxid.
        """

        base = Xref.objects.filter(upi=self.upi)
        xrefs = base.filter(deleted='N')
        if taxid is not None:
            xrefs = xrefs.filter(taxid=taxid)

        if not xrefs.exists():
            xrefs = base
            if taxid is not None:
                xrefs = xrefs.filter(taxid=taxid)

        return xrefs.select_related('accession', 'db')

    def has_rfam_hits(self):
        """
        Check if this has any Rfam hits.

        :returns bool: True if there are any Rfam matches.
        """
        return bool(self.get_rfam_hits())

    def get_rfam_hits(self, allow_suppressed=True):
        """
        This gets all matches of this Rna to any Rfam hit. Note that this does
        not exclude any families which are supressed. If two families from the
        same clan hit the same sequence then this will selec the hit with the
        lowest e-value and highest score.

        :returns list: A list of all Rfam hits to this sequence.
        """

        query = RfamHit.objects.filter(upi=self.upi)
        if not allow_suppressed:
            query = query.filter(rfam_model__is_suppressed=False)
        return query.order_by('rfam_model_id', 'sequence_start')

    def grouped_rfam_hits(self, allow_suppressed=True):
        hits = it.groupby(
            self.get_rfam_hits(allow_suppressed=allow_suppressed),
            op.attrgetter('rfam_model_id')
        )
        results = []
        for _, hits in hits:
            hits = list(hits)
            ranges = []
            for hit in hits:
                ranges.append((
                    hit.sequence_start,
                    hit.sequence_stop,
                    hit.model_completeness,
                ))

            results.append({
                'raw': hits,
                'ranges': ranges,
                'rfam_model': hits[0].rfam_model,
                'rfam_model_id': hits[0].rfam_model_id,
            })
        return sorted(results, key=lambda h: h['ranges'][0][0])

    def get_rfam_status(self, taxid=None):
        return check_issues(self, taxid=taxid)

    def was_rfam_analyzed(self):
        """
        Check if this Rna was analyzed with Rfam. This does not check if there
        are matches, because some sequences will have no match even when
        analyzed, so this looks at the RfamAnalyzedSequences table for this
        information.

        :returns bool: True if this was ever analyzed with Rfam.
        """

        has = bool(RfamAnalyzedSequences.objects.get(upi=self.upi))
        return has

    def get_domains(self, taxid=None, ignore_unclassified=False):
        """
        Get all domains this sequence has been found in. If taxid is given then
        only the domain for all accessions from the given taxid will be
        returned. If ignore_unclassified is given then this will exclude any
        domains where the organism comes from an enviromental sample or is
        uncultured.
        """

        domains = set()
        accessions = Accession.objects.filter(xrefs__upi=self.upi)
        if taxid:
            accessions = accessions.filter(xrefs__taxid=taxid)
        for accession in accessions:
            classification = accession.classification
            if ignore_unclassified:
                if 'uncultured' in classification or \
                        'environmental' in classification:
                    continue
            domains.add(classification.split(';')[0])
        return domains
