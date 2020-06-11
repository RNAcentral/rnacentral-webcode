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

import re

from django.db import models
from django.db.models import Min, Max
from rest_framework.renderers import JSONRenderer
from caching.base import CachingMixin, CachingManager

from .accession import Accession
from .ensembl_assembly import EnsemblAssembly


class RawSqlQueryset(models.QuerySet):
    """
    We override the default queryset to annotate each queryset object
    with database-specific fields, obtained via raw SQL queries, when
    queryset is actually evaluated (queryset is evaluated when its
    _fetch_all() method is called). So, we override that method to
    add some extra fields, obtained by raw SQL queries.
    """

    def _get_taxid(self):
        """
        This is a dirty-dirty hack that checks, if taxid filter is applied
        to this queryset, and if it is, extracts taxid from django internals,
        otherwise, returns None.

        Used to provide taxid to raw SQL queries, issued by _fetch_all().

        Dirty implementation details:
         * self.query is a python object, used to actually construct raw SQL.
         * self.query.where is a WhereNode, extending django.utils.Node,
             it's a tree node. queryset.filter() expressions are stored as tree
             nodes on WhereNode objects.
         * self.query.where.children stores children of current node.
         * self.query.where.children[0].lhs is a lookup - Col object - where
             Col.target knows what field to lookup.
         * self.query.were.children[0].rhs contains lookup value.
        """
        from django.db.models.lookups import Exact

        taxid = None
        for child in self.query.where.children:
            if isinstance(child, Exact) and str(child.lhs.target) == 'portal.Xref.taxid':
                taxid = child.rhs
        return taxid

    def _fetch_all(self):
        """
        This method performs the actual database lookup, when queryset is evaluated.
        We extend it to fetch database-specific data with raw SQL queries.
        """
        super(RawSqlQueryset, self)._fetch_all()

        # check this flag to avoid infinite recursion loop with _fetch_all() called by get_mirbase_mature_products()
        if not hasattr(self, "fetch_all_already_called"):

            # set this flag to avoid infinite recursion loop
            self.fetch_all_already_called = True

            # add database-specific fields only if this queryset contains model objects
            # (this is not the case for values() or values_list() methods)
            if len(self) and type(self[0]) == Xref:

                taxid = self._get_taxid()

                # Raw SQL queries to fetch database-specific data with self-joins, impossible in Django ORM
                mirbase_mature_products = self.get_mirbase_mature_products(taxid)
                mirbase_precursors = self.get_mirbase_precursor(taxid)
                refseq_mirna_mature_products = self.get_refseq_mirna_mature_products(taxid)
                refseq_mirna_precursors = self.get_refseq_mirna_precursor(taxid)
                refseq_splice_variants = self.get_refseq_splice_variants(taxid)
                ensembl_splice_variants = self.get_ensembl_splice_variants(taxid)
                tmrna_mates = self.get_tmrna_mate(taxid)

                # "annotate" xrefs queryset with additional attributes, retrieved by raw SQL queries
                for xref in self:
                    if xref.id in mirbase_mature_products:
                        xref.mirbase_mature_products = [ mature_product.upi.upi for mature_product in mirbase_mature_products[xref.id] ]
                    if xref.id in mirbase_precursors:
                        xref.mirbase_precursor = mirbase_precursors[xref.id][0].upi.upi  # note, there's just 1 precursor
                    if xref.id in refseq_mirna_mature_products:
                        xref.refseq_mirna_mature_products = [ mature_product.upi.upi for mature_product in refseq_mirna_mature_products[xref.id] ]
                    if xref.id in refseq_mirna_precursors:
                        xref.refseq_mirna_precursor = refseq_mirna_precursors[xref.id][0].upi.upi  # note, there's just 1 precursor
                    if xref.id in refseq_splice_variants:
                        xref.refseq_splice_variants = [ splice_variant.upi.upi for splice_variant in refseq_splice_variants[xref.id] ]
                    if xref.id in ensembl_splice_variants:
                        xref.ensembl_splice_variants = [ splice_variant.upi.upi for splice_variant in ensembl_splice_variants[xref.id] ]
                    if xref.id in tmrna_mates:
                        xref.tmrna_mates = [ tmrna_mate.upi.upi for tmrna_mate in tmrna_mates[xref.id] ]

    def _xrefs_raw_queryset_to_dict(self, raw_queryset):
        """
        We convert it into a single dict, aggregate those iterables into a
        :param raw_queryset: iterable of dicts, returned by Xref.object.raw()
        :return: dict { Xref.pk: Xref (a single item of raw queryset) }
        """
        output_dict = {}
        for xref in raw_queryset:
            if xref.xid not in output_dict:
                output_dict[xref.xid] = [xref]
            else:
                output_dict[xref.xid].append(xref)
        return output_dict

    def get_mirbase_mature_products(self, taxid=None):
        if hasattr(self, 'accession'):
            if self.accession.database != 'mirbase'.upper():
                return None
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])  # e.g. "'250381225', '250381243', '295244525'"

        queryset = """
            SELECT xref.*, rnc_accessions.external_id
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND rnc_accessions.database = 'MIRBASE'
              AND rnc_accessions.feature_name = 'precursor_RNA'
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.external_id = x.external_id
            WHERE rnc_accessions.database = 'MIRBASE'
              AND rnc_accessions.feature_name = 'ncRNA'
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_mirbase_precursor(self, taxid=None):
        if hasattr(self, 'accession'):
            if self.accession.database != 'mirbase'.upper():
                return None
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.external_id
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND rnc_accessions.database = 'MIRBASE'
              AND rnc_accessions.feature_name = 'ncRNA'
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.external_id = x.external_id
            WHERE rnc_accessions.database = 'MIRBASE'
              AND rnc_accessions.feature_name = 'precursor_RNA'
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_refseq_mirna_mature_products(self, taxid=None):
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.parent_ac
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND rnc_accessions.database = 'REFSEQ'
              AND rnc_accessions.feature_name = 'precursor_RNA'
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.parent_ac = x.parent_ac
            WHERE rnc_accessions.database = 'REFSEQ'
              AND rnc_accessions.feature_name = 'ncRNA'
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_refseq_mirna_precursor(self, taxid=None):
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.parent_ac
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND xref.dbid = 9
              AND rnc_accessions.feature_name = 'ncRNA'
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.parent_ac = x.parent_ac
            WHERE xref.dbid = 9
              AND rnc_accessions.feature_name = 'precursor_RNA'
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_refseq_splice_variants(self, taxid=None):
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.ncrna_class, rnc_accessions.optional_id
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND xref.dbid = 9
              AND rnc_accessions.optional_id != ''
              AND (rnc_accessions.ncrna_class != 'miRNA' OR rnc_accessions.feature_name = 'precursor_RNA')
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.optional_id = x.optional_id
            WHERE xref.dbid = 9
              AND xref.deleted = 'N'
              AND rnc_accessions.accession != x.ac
              AND (rnc_accessions.ncrna_class != 'miRNA' OR rnc_accessions.feature_name = 'precursor_RNA')
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_ensembl_splice_variants(self, taxid=None):
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.optional_id
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.dbid = 25
              AND rnc_accessions.optional_id != ''
              AND (rnc_accessions.ncrna_class != 'miRNA' OR rnc_accessions.feature_name = 'precursor_RNA')
              AND xref.id IN ({pks})
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.optional_id = x.optional_id
            WHERE xref.dbid = 25
              AND xref.deleted = 'N'
              AND rnc_accessions.accession != x.ac
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)

    def get_tmrna_mate(self, taxid=None):
        taxid_filter = "AND xref.taxid = %s" % taxid if taxid else ""

        # _fetch_all() has already been called by now
        pks = ','.join(["'%s'" % xref.pk for xref in self])

        queryset = """
            SELECT xref.*, rnc_accessions.optional_id, rnc_accessions.database
            FROM xref, rnc_accessions
            WHERE xref.ac = rnc_accessions.accession
              AND xref.id IN ({pks})
              AND rnc_accessions.database = 'TMRNA_WEB'
              AND rnc_accessions.optional_id IS NOT NULL
              {taxid_filter}
        """.format(pks=pks, taxid_filter=taxid_filter)

        annotated_queryset = """
            SELECT xref.*, x.id as xid
            FROM xref
            JOIN rnc_accessions
            ON xref.ac = rnc_accessions.accession
            JOIN (
              {queryset}
            ) x
            ON rnc_accessions.parent_ac = x.optional_id
            WHERE rnc_accessions.is_composite = 'Y'
              {taxid_filter}
        """.format(queryset=queryset, taxid_filter=taxid_filter)

        raw_queryset = Xref.objects.raw(annotated_queryset)

        return self._xrefs_raw_queryset_to_dict(raw_queryset)


class RawSqlXrefManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return RawSqlQueryset(self.model, using=self._db)


class Xref(CachingMixin, models.Model):
    id = models.AutoField(primary_key=True)
    db = models.ForeignKey("Database", db_column='dbid', related_name='xrefs')
    accession = models.ForeignKey("Accession", db_column='ac', to_field='accession', related_name='xrefs', unique=True)
    created = models.ForeignKey("Release", db_column='created', related_name='release_created')
    last = models.ForeignKey("Release", db_column='last', related_name='last_release')
    upi = models.ForeignKey("Rna", db_column='upi', to_field='upi', related_name='xrefs')
    version_i = models.IntegerField()
    deleted = models.CharField(max_length=1)
    timestamp = models.DateTimeField()
    userstamp = models.CharField(max_length=100)
    version = models.IntegerField()
    taxid = models.IntegerField()

    objects = RawSqlXrefManager()
    default_objects = CachingManager()

    class Meta:
        db_table = 'xref'

    def has_modified_nucleotides(self):
        """Determine whether an xref has modified nucleotides."""
        return self.modifications.count() > 0

    def get_distinct_modifications(self):
        """Get a list of distinct modified nucleotides described in this xref."""
        modifications = []
        seen = None
        for modification in self.modifications.order_by('modification_id').all():
            if modification.modification_id == seen:
                continue
            else:
                modifications.append(modification)
                seen = modification.modification_id
        return modifications

    def get_modifications_as_json(self):
        """
        Get a JSON object listing all modified positions and the chemical
        components. This object is used for visualising modified nucleotides
        in the UI.
        """
        import apiv1.serializers
        serializer = apiv1.serializers.ModificationSerializer(self.modifications.all(), many=True)
        return JSONRenderer().render(serializer.data)

    def is_active(self):
        """Convenience method for determining whether an xref is current or obsolete."""
        return self.deleted == 'N'

    def is_rfam_seed(self):
        """Determine whether an xref is part of a manually curated RFAM seed alignment."""
        if self.accession.note:
            return re.search('alignment\:seed', self.accession.note, re.IGNORECASE) is not None
        else:
            return False

    def get_ncbi_gene_id(self):
        """GeneID links are stored in the optional_id field."""
        if self.accession.optional_id:
            match = re.search('GeneID\:(\d+)', self.accession.optional_id, re.IGNORECASE)
            return match.group(1) if match else None
        else:
            return None

    def get_ndb_external_url(self):
        """
        For some entries NDB uses different ids than those assigned by the PDB.
        NDB ids are store in the db_xref column.
        This function returns an NDB url using NDB ids where possible
        with PDB ids used as a fallback.
        """
        if self.accession.database == 'PDBE':
            ndb_url = 'http://ndbserver.rutgers.edu/service/ndb/atlas/summary?searchTarget={structure_id}'
            if self.accession.db_xref:
                match = re.search('NDB\:(\w+)', self.accession.db_xref, re.IGNORECASE)
                if match:
                    structure_id = match.group(1)  # NDB id
                else:
                    structure_id = self.accession.external_id  # default to PDB id
                return ndb_url.format(structure_id=structure_id)
            else:
                return None
        else:
            return None

    def is_mirbase_mirna_precursor(self):
        """True if the accession is a miRBase precursor miRNA."""
        return self.accession.feature_name == 'precursor_RNA' and self.accession.database == 'MIRBASE'

    def get_mirbase_mature_products_if_any(self):
        return self.get_mirbase_mature_products() if self.is_mirbase_mirna_precursor() else []

    def get_mirbase_mature_products(self):
        """miRBase mature products and precursors share the same external MI* identifier."""
        mature_products = Xref.objects.filter(
            accession__external_id=self.accession.external_id,
            accession__feature_name='ncRNA'
        ).all()

        upis = []
        for mature_product in mature_products:
            upis.append(mature_product.upi)

        return upis

    def get_mirbase_precursor(self):
        """miRBase mature products and precursors share the same external MI* identifier."""
        if self.accession.database != 'mirbase'.upper():
            return None
        else:
            precursor = Xref.objects.filter(
                accession__external_id=self.accession.external_id,
                accession__feature_name='precursor_RNA'
            ).first()

            return precursor.upi.upi if precursor else None

    def is_refseq_mirna(self):
        """
        RefSeq miRNAs are stored in 3 xrefs:
            * precursor_RNA
            * 5-prime ncRNA
            * 3-prime ncRNA
        which share the same parent accession.
        """
        same_parent = Xref.objects.filter(
            accession__parent_ac=self.accession.parent_ac,
            accession__ncrna_class='miRNA',
            deleted=self.deleted
        ).all()

        return len(same_parent) > 0

    def get_refseq_mirna_mature_products_if_any(self):
        return self.get_refseq_mirna_mature_products() if self.is_refseq_mirna() else []

    def get_refseq_mirna_mature_products(self):
        """Given a precursor miRNA, retrieve its mature products."""
        mature_products = Xref.objects.filter(
            accession__parent_ac=self.accession.parent_ac,
            accession__feature_name='ncRNA'
        ).all()

        upis = []
        for mature_product in mature_products:
            upis.append(mature_product.upi)
        return upis

    def get_refseq_mirna_precursor(self):
        """Given a 5-prime or 3-prime mature product, retrieve its precursor miRNA."""
        if self.accession.feature_name != 'precursor_RNA':
            rna = Xref.objects.filter(
                accession__parent_ac=self.accession.parent_ac,
                accession__feature_name='precursor_RNA'
            ).first()

            if rna:
                return rna.upi
        return None

    def get_refseq_splice_variants(self):
        """
        RefSeq splice variants are identified by the same GeneID.
        Example: URS000075D687.
        """
        splice_variants = []
        gene_id = self.get_ncbi_gene_id()
        if gene_id:
            xrefs = Xref.objects.filter(
                db__display_name='RefSeq',
                deleted='N',
                accession__ncrna_class=self.accession.ncrna_class,
                accession__db_xref__iregex='GeneId:'+gene_id
            ).exclude(accession=self.accession.accession).all()

            for splice_variant in xrefs:
                splice_variants.append(splice_variant.upi)
            splice_variants.sort(key=lambda x: x.length)
        return splice_variants

    def get_tmrna_mate_upi(self):
        """Get the mate of the 2-piece tmRNA"""
        # TODO: Currently this function is not used anywhere in the code.
        # TODO: Moreover, it doesn't work, because self.accession.optional_id
        # TODO: is always None for all the records from rmRNA Website.
        if self.db.display_name != 'tmRNA Website':
            tmrna_mate_upi = False
        if not self.accession.optional_id:  # no mate info
            tmrna_mate_upi = False
        try:
            mate = Accession.objects.filter(parent_ac=self.accession.optional_id, is_composite='Y').get()
        except Accession.DoesNotExist:
            return False

        tmrna_mate_upi = mate.xrefs.get().upi.upi
        return tmrna_mate_upi

    def get_tmrna_type(self):
        """
        Possible tmRNA types:
            * acceptor (tRNA-like domain)
            * coding (mRNA-like domain),
            * precursor (contains the acceptor and coding sequences and other intervening sequences)
        """
        tmrna_type = 0
        if self.db.display_name != 'tmRNA Website':
            tmrna_type = 0  # not tmRNA
        if not self.accession.optional_id:
            tmrna_type = 1  # one-piece or precursor
        else:
            tmrna_type = 2  # two-piece tmRNA
        return tmrna_type

    def get_gencode_transcript_id(self):
        """
        GENCODE entries have their corresponding Ensembl transcript ids stored
        in Accession.accession. Example:
        {"transcript_id": ["GENCODE:ENSMUST00000160979.8"]}
        """
        if self.db.display_name == 'GENCODE':
            if self.accession.accession.startswith('GENCODE:'):
                return self.accession.accession.split(':')[1]
            elif self.accession.accession.startswith('ENSMUST'):
                return self.accession.accession
            else:
                return None
        else:
            return None

    def get_gencode_ensembl_url(self):
        """Get Ensembl URL for GENCODE transcripts."""
        ensembl_transcript_id = self.get_gencode_transcript_id()
        if ensembl_transcript_id:
            url = 'http://ensembl.org/{species}/Transcript/Summary?db=core;t={id}'.format(
                id=ensembl_transcript_id,
                species=self.accession.species.replace(' ', '_')
            )
            return url
        else:
            return None

    def get_ensembl_division(self):
        """Get Ensembl or Ensembl Genomes division for the cross-reference."""
        try:
            assembly = EnsemblAssembly.objects.get(taxid=self.taxid)
            return {'name': assembly.division, 'url': 'http://' + assembly.subdomain}
        except EnsemblAssembly.DoesNotExist:
            return None

    def get_ucsc_db_id(self):
        """Get UCSC id for the genome assembly. http://genome.ucsc.edu/FAQ/FAQreleases.html"""
        try:
            genome = EnsemblAssembly.objects.get(taxid=self.taxid)
            return genome.assembly_ucsc
        except EnsemblAssembly.DoesNotExist:
            return None
