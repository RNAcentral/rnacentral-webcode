"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Min, Max
from django.utils.functional import cached_property
from caching.base import CachingManager, CachingMixin # django-cache-machine
from portal.config.genomes import genomes as rnacentral_genomes
from portal.config.expert_databases import expert_dbs as rnacentral_expert_dbs
import json
import re

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


class Modification(CachingMixin, models.Model):
    """
    Describe modified nucleotides at certain sequence positions reported in xrefs.
    """
    id = models.AutoField(primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', related_name='modifications')
    xref = models.ForeignKey('Xref', db_column='accession', to_field='accession', related_name='modifications')
    position = models.PositiveIntegerField() # absolute sequence position, always > 0
    author_assigned_position = models.IntegerField() # can be negative, e.g. 3I2S chain A
    modification_id = models.ForeignKey('ChemicalComponent', db_column='modification_id')

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_modifications'


class ChemicalComponent(CachingMixin, models.Model):
    """
    List of all possible nucleotide modifications.
    """
    id = models.CharField(max_length=8, primary_key=True)
    description = models.CharField(max_length=500)
    one_letter_code = models.CharField(max_length=1)
    ccd_id = models.CharField(max_length=3, default='') # Chemical Component Dictionary id
    source = models.CharField(max_length=10, default='') # Modomics, PDBe, others
    modomics_short_name = models.CharField(max_length=20, default='') # m2A for 2A

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_chemical_components'

    def get_pdb_url(self):
        """
        Get a link to PDB Chemical Component Dictionary from PDB entries and
        Modomics entries that are mapped to PDB.
        """
        pdb_url = 'http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/{id}'
        if self.source == 'PDB':
            return pdb_url.format(id=self.id)
        elif self.source == 'Modomics' and self.ccd_id:
            return pdb_url.format(id=self.ccd_id)
        else:
            return None

    def get_modomics_url(self):
        """
        Get a link to Modomics modifications.
        """
        if self.source == 'Modomics':
            return 'http://modomics.genesilico.pl/modifications/{id}'.format(id=self.modomics_short_name)
        else:
            return None


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
        """
        Get a URL for an RNA object.
        Used for generating sitemaps.
        """
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
        ORDER BY b.title"""
        if taxid:
            query = query.format(taxid_clause='t1.taxid = %s AND' % taxid)
        else:
            query = query.format(taxid_clause='')
        return Reference.objects.raw(query, [self.upi])

    def is_active(self):
        """
        A sequence is considered active if it has at least one active cross_reference.
        """
        deleted = self.xrefs.values_list('deleted', flat=True).distinct()
        if 'N' in deleted:
            return True
        else:
            return False

    def has_genomic_coordinates(self, taxid=None):
        """
        Return True if at least one cross-reference has genomic coordinates.
        """
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
        seq = self.get_sequence()
        count_A = seq.count('A')
        count_C = seq.count('C')
        count_G = seq.count('G')
        count_U = seq.count('U')
        return {
            'A': count_A,
            'U': count_U,
            'C': count_C,
            'G': count_G,
            'N': len(seq) - (count_A + count_C + count_G + count_U)
        }

    def get_xrefs(self, taxid=None):
        """
        Get all xrefs, show non-ENA annotations first.
        Exclude source ENA entries that are associated with other expert db entries.
        For example, only fetch Vega xrefs and don't retrieve the ENA entries they are
        based on.
        """
        expert_db_projects = Database.objects.exclude(project_id=None).\
                                              values_list('project_id', flat=True)
        xrefs = self.xrefs.filter(deleted='N', upi=self.upi).\
                           exclude(db__id=1, accession__project__in=expert_db_projects).\
                           order_by('-db__id').\
                           select_related()
        if taxid:
            xrefs = xrefs.filter(taxid=taxid)
        if xrefs.exists():
            return xrefs
        else:
            return self.xrefs.filter(deleted='Y').select_related()

    def count_xrefs(self):
        """
        Count the number of cross-references associated with the sequence.
        """
        return self.xrefs.filter(db__project_id__isnull=True, deleted='N').count()

    @cached_property
    def count_distinct_organisms(self):
        """
        Count the number of distinct taxids referenced by the sequence.
        """
        queryset = self.xrefs.values('accession__species')
        results = queryset.filter(deleted='N').distinct().count()
        if not results:
            results = queryset.distinct().count()
        return results

    def get_distinct_database_names(self, taxid=None):
        """
        Get a non-redundant list of databases referencing the sequence.
        """
        databases = self.xrefs.filter(deleted='N')
        if taxid:
            databases = databases.filter(taxid=taxid)
        databases = list(databases.values_list('db__display_name', flat=True).distinct())
        databases = sorted(databases, key=lambda s: s.lower()) # case-insensitive
        return databases

    @cached_property
    def first_seen(self):
        """
        Return the earliest release the sequence is referenced in.
        """
        data = self.xrefs.aggregate(first_seen=Min('created__release_date'))
        return data['first_seen']

    @cached_property
    def last_seen(self):
        """
        Like `first_seen` but with reversed order.
        """
        data = self.xrefs.aggregate(last_seen=Max('last__release_date'))
        return data['last_seen']

    def get_sequence_fasta(self):
        """
        Split long sequences by a fixed number of characters per line.
        """
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
        """
        Format genomic coordinates from all xrefs into a single file in GFF3 format.
        """
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

    def xref_with_taxid_exists(self, taxid):
        """
        Return True if the Rna has xrefs with a given taxid.
        """
        if self.xrefs.filter(taxid=taxid).exists():
            return True
        else:
            return False

    def get_description(self, taxid=None, recompute=False):
        """
        Get entry description based on its xrefs.
        If taxid is provided, use only species-specific xrefs.
        """
        def count_distinct_descriptions():
            """
            Count distinct description lines.
            """
            queryset = xrefs.values_list('accession__description', flat=True)
            results = queryset.filter(deleted='N').distinct().count()
            if not results:
                results = queryset.distinct().count()
            return results

        def get_distinct_products():
            """
            Get distinct non-null product values as a list.
            """
            queryset = xrefs.values_list('accession__product', flat=True).\
                             filter(accession__product__isnull=False)
            results = queryset.filter(deleted='N').distinct()
            if not results:
                results = queryset.distinct()
            return results

        def get_distinct_genes():
            """
            Get distinct non-null gene values as a list.
            """
            queryset = xrefs.values_list('accession__gene', flat=True).\
                             filter(accession__gene__isnull=False)
            results = queryset.filter(deleted='N').distinct()
            if not results:
                results = queryset.distinct()
            return results

        def get_distinct_feature_names():
            """
            Get distinct feature names as a list.
            """
            queryset = xrefs.values_list('accession__feature_name', flat=True)
            results = queryset.filter(deleted='N').distinct()
            if not results:
                results = queryset.distinct()
            return results

        def get_distinct_ncrna_classes():
            """
            For ncRNA features, get distinct ncrna_class values as a list.
            """
            queryset = xrefs.values_list('accession__ncrna_class', flat=True).\
                             filter(accession__ncrna_class__isnull=False)
            results = queryset.filter(deleted='N').distinct()
            if not results:
                results = queryset.distinct()
            return results

        def get_rna_type():
            """
            product > gene > feature name
            For ncRNA features, use ncrna_class annotations.
            """
            products = get_distinct_products()
            genes = get_distinct_genes()
            if len(products) == 1:
                rna_type = products[0]
            elif len(genes) == 1:
                rna_type = genes[0]
            else:
                feature_names = get_distinct_feature_names()
                if feature_names[0] == 'ncRNA' and len(feature_names) == 1:
                    ncrna_classes = get_distinct_ncrna_classes()
                    rna_type = '/'.join(ncrna_classes)
                else:
                    rna_type = '/'.join(feature_names)
            return rna_type

        def get_urs_description():
            """
            Get a description for a URS identifier, including multiple species.
            """
            if count_distinct_descriptions() == 1:
                description_line = xrefs.first().accession.description
                description_line = description_line[0].upper() + description_line[1:]
            else:
                rna_type = get_rna_type()
                distinct_species = self.count_distinct_organisms
                if taxid or distinct_species == 1:
                    species = xrefs.first().accession.species
                    description_line = '{species} {rna_type}'.format(
                                        species=species, rna_type=rna_type)
                else:
                    description_line = ('{rna_type} from '
                                        '{distinct_species} species').format(
                                        rna_type=rna_type,
                                        distinct_species=distinct_species)
            return description_line

        def get_xrefs_for_description(taxid):
            """
            Get cross-references for building a description line.
            """
            # try only active xrefs first
            if taxid:
                xrefs = self.xrefs.filter(deleted='N', taxid=taxid)
            else:
                xrefs = self.xrefs.filter(deleted='N')
            # fall back onto all xrefs if no active ones are found
            if not xrefs.exists():
                if taxid:
                    xrefs = self.xrefs.filter(taxid=taxid)
                else:
                    xrefs = self.xrefs.filter()
            return xrefs.select_related('accession').\
                         prefetch_related('accession__refs', 'accession__coordinates')

        def score_xref(xref):
            """
            Return a score for a cross-reference based on its metadata.
            """
            def get_genome_bonus():
                """
                Find if the xref has genome mapping.
                Iterate over prefetched queryset to avoid hitting the database.
                """
                chromosomes = []
                for coordinate in xref.accession.coordinates.all():
                    chromosomes.append(coordinate.chromosome)
                if not chromosomes:
                    return 0
                else:
                    return 1

            paper_bonus = xref.accession.refs.count() * 0.2
            genome_bonus = get_genome_bonus()
            gene_bonus = 0
            note_bonus = 0
            product_bonus = 0
            rfam_full_alignment_penalty = 0
            misc_rna_penalty = 0

            if xref.accession.product:
                product_bonus = 0.1
            if xref.accession.gene:
                gene_bonus = 0.1
            if xref.db_id == 2 and not xref.is_rfam_seed():
                rfam_full_alignment_penalty = -2
            if xref.accession.feature_name == 'misc_RNA':
                misc_rna_penalty = -2
            if xref.accession.note:
                note_bonus = 0.1

            score = paper_bonus + \
                genome_bonus + \
                gene_bonus + \
                product_bonus + \
                note_bonus + \
                rfam_full_alignment_penalty + \
                misc_rna_penalty
            return score

        if not recompute:
            if taxid:
                queryset = RnaPrecomputed.objects.filter(taxid=taxid)
            else:
                queryset = RnaPrecomputed.objects.filter(taxid__isnull=True)
            try:
                obj = queryset.get(upi=self.upi)
            except ObjectDoesNotExist:
                obj = None
            if obj:
                return obj.description
        # get description
        if taxid and not self.xref_with_taxid_exists(taxid):
            taxid = None # ignore taxid
        xrefs = get_xrefs_for_description(taxid)
        if not taxid:
            return get_urs_description()
        else:
            # pick one of expert database descriptions
            scores = []
            for xref in xrefs:
                scores.append((score_xref(xref), xref.accession.description))
            scores.sort(key=lambda tup: tup[0], reverse=True)
            return scores[0][1]


class RnaPrecomputed(models.Model):
    """
    """
    id = models.CharField(max_length=22, primary_key=True)
    upi = models.ForeignKey('Rna', db_column='upi', to_field='upi', related_name='precomputed')
    taxid = models.IntegerField(db_index=True, null=True)
    description = models.CharField(max_length=250)

    class Meta:
        db_table = 'rnc_rna_precomputed'


class DatabaseStats(models.Model):
    """
    These data are kept in a separate table because accessing CLOBs is slow,
    and this table will only be loaded when necessary.
    """
    database = models.CharField(max_length=30, primary_key=True)
    length_counts = models.TextField()
    taxonomic_lineage = models.TextField()

    class Meta:
        db_table = 'rnc_database_json_stats'


class Database(CachingMixin, models.Model):
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.CharField(max_length=30)
    current_release = models.IntegerField()
    full_descr = models.CharField(max_length=255)
    alive = models.CharField(max_length=1)
    for_release = models.CharField(max_length=1)
    display_name = models.CharField(max_length=40)
    url = models.CharField(max_length=100)
    project_id = models.CharField(max_length=10)
    avg_length = models.IntegerField()
    min_length = models.IntegerField()
    max_length = models.IntegerField()
    num_sequences = models.IntegerField()
    num_organisms = models.IntegerField()

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_database'

    def count_sequences(self):
        """
        Count unique sequences associated with the database.
        """
        return self.xrefs.values_list('upi', flat=True).distinct().count()

    def count_organisms(self):
        """
        Count distinct taxids associated with the database.
        """
        return self.xrefs.values_list('taxid', flat=True).distinct().count()

    def first_imported(self):
        """
        Get the earliest imported date.
        """
        return self.xrefs.order_by('timestamp').first().timestamp

    @cached_property
    def description(self):
        """
        Get database description.
        """
        return self.__get_database_attribute(self.display_name, 'description')

    @cached_property
    def label(self):
        """
        Get database slugified label.
        """
        return self.__get_database_attribute(self.display_name, 'label')

    @cached_property
    def examples(self):
        """
        Get database examples.
        """
        return self.__get_database_attribute(self.display_name, 'examples')

    def references(self):
        """
        Get literature references.
        """
        return self.__get_database_attribute(self.display_name, 'references')

    @cached_property
    def url(self):
        """
        Get database url.
        """
        return self.__get_database_attribute(self.display_name, 'url')

    @cached_property
    def abbreviation(self):
        """
        Get database name abbreviation.
        """
        return self.__get_database_attribute(self.display_name, 'abbreviation')

    @cached_property
    def name(self):
        """
        Get database display name. This is safer than using self.display_name
        because it doesn't require updating the database field.
        """
        return self.__get_database_attribute(self.display_name, 'name')

    @cached_property
    def status(self):
        """
        Get the status of the database (new/updated/etc).
        """
        return self.__get_database_attribute(self.display_name, 'status')

    @cached_property
    def version(self):
        """
        Get database version (Rfam 12, PDB as of date etc).
        """
        return self.__get_database_attribute(self.display_name, 'version')

    def __get_database_attribute(self, db_name, attribute):
        """
        An accessor method for retrieving attributes from a list.
        """
        return [x[attribute] for x in rnacentral_expert_dbs if x['name'].lower() == db_name.lower()].pop()

    def get_absolute_url(self):
        """
        Get a URL for a Database object.
        Used for generating sitemaps.
        """
        return reverse('expert-database', kwargs={'expert_db_name': self.label})


class Release(CachingMixin, models.Model):
    db = models.ForeignKey(Database, db_column='dbid', related_name='db')
    release_date = models.DateField()
    release_type = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    descr = models.TextField()
    force_load = models.CharField(max_length=1)

    objects = CachingManager()

    def get_release_type(self):
        return 'full' if self.release_type == 'F' else 'incremental'

    class Meta:
        db_table = 'rnc_release'


class Accession(models.Model):
    accession = models.CharField(max_length=100, primary_key=True)
    parent_ac = models.CharField(max_length=100)
    seq_version = models.IntegerField(db_index=True)
    feature_start = models.IntegerField(db_index=True)
    feature_end = models.IntegerField(db_index=True)
    feature_name = models.CharField(max_length=20)
    ordinal = models.IntegerField()
    division = models.CharField(max_length=3)
    keywords = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    species = models.CharField(max_length=150)
    organelle = models.CharField(max_length=100)
    classification = models.CharField(max_length=500)
    project = models.CharField(max_length=50)
    is_composite = models.CharField(max_length=1)
    non_coding_id = models.CharField(max_length=100)
    database = models.CharField(max_length=20)
    external_id = models.CharField(max_length=150)
    optional_id = models.CharField(max_length=100)
    anticodon = models.CharField(max_length=50)
    experiment = models.CharField(max_length=500)
    function = models.CharField(max_length=500)
    gene = models.CharField(max_length=50)
    gene_synonym = models.CharField(max_length=400)
    inference = models.CharField(max_length=100)
    locus_tag = models.CharField(max_length=50)
    genome_position = models.CharField(max_length=200, db_column='map')
    mol_type = models.CharField(max_length=50)
    ncrna_class = models.CharField(max_length=50)
    note = models.CharField(max_length=1500)
    old_locus_tag = models.CharField(max_length=50)
    product = models.CharField(max_length=300)
    db_xref = models.CharField(max_length=100)
    standard_name = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'rnc_accessions'

    def get_pdb_entity_id(self):
        """
        Example PDB accession: 1J5E_A_1 (PDB id, chain, entity id)
        """
        if self.database == 'PDBE':
            return self.accession.split('_')[-1]
        return None

    def get_pdb_structured_note(self):
        """
        Get 3D structure metadata stored in a structured note.
        * experimental technique
        * PDB structure title
        * release date
        """
        note = json.loads(self.note)
        return note

    def get_hgnc_id(self):
        """
        Search db_xref field for an HGNC id.
        """
        hgnc_id = ''
        match = re.search(r'HGNC\:HGNC\:(\d+)', self.db_xref)
        if match:
            hgnc_id = match.group(1)
        return hgnc_id

    def get_biotype(self):
        """
        Biotype annotations are stored in notes and come from Ensembl and VEGA
        entries.
        Biotype is used to color entries in Genoverse.
        If biotype contains the word "RNA" it is given a predefined color.
        """
        biotype = 'ncRNA' # default biotype
        match = re.search(r'biotype\:(\w+)', self.note)
        if match:
            biotype = match.group(1)
        return biotype

    def get_rna_type(self):
        """
        Get the type of RNA, which either the name of the feature from the
        feature table in the Non-coding product, or for `ncRNA` features,
        it's one of the ncRNA classes defined by INSDC.
        """
        if self.feature_name == 'ncRNA':
            return self.ncrna_class
        else:
            return self.feature_name

    def get_srpdb_id(self):
        return re.sub('\.\d+$', '', self.external_id)

    def get_ena_url(self):
        """
        Get the ENA entry url that refers to the entry from
        the Non-coding product containing the cross-reference.
        """
        if self.database in ['RFAM', 'PDBE', 'REFSEQ', 'RDP']:
            return '' # no ENA source links for these entries
        ena_base_url = "http://www.ebi.ac.uk/ena/data/view/Non-coding:"
        if self.is_composite == 'Y':
            return ena_base_url + self.non_coding_id
        else:
            return ena_base_url + self.accession

    def get_vega_transcript_url(self):
        """
        Get external url for Vega transcripts.
        """
        url = 'http://vega.sanger.ac.uk/{species}/Transcript/Summary?db=core;t={id}'.format(
            id=self.external_id, species=self.species.replace(' ', '_'))
        return url

    def get_expert_db_external_url(self):
        """
        Get external url to expert database.
        """
        urls = {
            'RFAM': 'http://rfam.xfam.org/family/{id}',
            'SRPDB': 'http://rnp.uthscsa.edu/rnp/SRPDB/rna/sequences/fasta/{id}',
            'VEGA': 'http://vega.sanger.ac.uk/{species}/Gene/Summary?db=core;g={id}',
            'MIRBASE': 'http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc={id}',
            'TMRNA_WEB': 'http://bioinformatics.sandia.gov/tmrna/seqs/{id}',
            'LNCRNADB': 'http://www.lncrnadb.org/{id}',
            'REFSEQ': 'http://www.ncbi.nlm.nih.gov/nuccore/{id}.{version}',
            'RDP': 'http://rdp.cme.msu.edu/hierarchy/detail.jsp?seqid={id}',
            'SNOPY': 'http://snoopy.med.miyazaki-u.ac.jp/snorna_db.cgi?mode=sno_info&id={id}',
            'PDBE': 'http://www.ebi.ac.uk/pdbe-srv/view/entry/{id}',
            'SGD': 'http://www.yeastgenome.org/locus/{id}/overview',
            'TAIR': 'http://www.arabidopsis.org/servlets/TairObject?id={id}&type=locus',
            'WORMBASE': 'http://www.wormbase.org/species/c_elegans/gene/{id}',
            'PLNCDB': 'http://chualab.rockefeller.edu/cgi-bin/gb2/gbrowse_details/arabidopsis?name={id}',
            'GTRNADB': 'http://lowelab.ucsc.edu/GtRNAdb/',
            'DICTYBASE': 'http://dictybase.org/gene/{id}',
            'SILVA': 'http://www.arb-silva.de/browser/{lsu_ssu}/silva/{id}',
            'POMBASE': 'http://www.pombase.org/spombe/result/{id}',
            'GREENGENES': 'http://www.ebi.ac.uk/ena/data/view/{id}.{version}',
            'NONCODE': 'http://www.bioinfo.org/NONCODEv4/show_rna.php?id={id}',
            'LNCIPEDIA': 'http://www.lncipedia.org/db/transcript/{id}',
            'MODOMICS': 'http://modomics.genesilico.pl/sequences/list/{id}',
        }
        if self.database in urls.keys():
            if self.database == 'GTRNADB':
                if 'summary' in self.external_id:
                    return urls[self.database] + self.external_id + '.html'
                else:
                    return urls[self.database] + self.external_id + '/' + self.external_id + '-summary.html'
            elif self.database == 'LNCRNADB':
                return urls[self.database].format(id=self.optional_id.replace(' ', ''))
            elif self.database == 'VEGA':
                return urls[self.database].format(id=self.optional_id,
                    species=self.species.replace(' ', '_'))
            elif self.database == 'SILVA':
                return urls[self.database].format(id=self.optional_id,
                    lsu_ssu='ssu' if 'small' in self.product else 'lsu')
            elif self.database == 'GREENGENES':
                return urls[self.database].format(id=self.parent_ac, version=self.seq_version)
            elif self.database == 'REFSEQ':
                return urls[self.database].format(id=self.external_id, version=self.seq_version)
            return urls[self.database].format(id=self.external_id)
        else:
            return ''


class GenomicCoordinates(models.Model):
    accession = models.ForeignKey('Accession', db_column='accession', to_field='accession', related_name='coordinates')
    primary_accession = models.CharField(max_length=50)
    local_start = models.IntegerField()
    local_end = models.IntegerField()
    chromosome = models.CharField(max_length=50, db_column='name')
    primary_start = models.IntegerField()
    primary_end = models.IntegerField()
    strand = models.IntegerField()

    class Meta:
        db_table = 'rnc_coordinates'


class Xref(models.Model):
    db = models.ForeignKey(Database, db_column='dbid', related_name='xrefs')
    accession = models.ForeignKey(Accession, db_column='ac', to_field='accession', related_name='xrefs', unique=True)
    created = models.ForeignKey(Release, db_column='created', related_name='release_created')
    last = models.ForeignKey(Release, db_column='last', related_name='last_release')
    upi = models.ForeignKey(Rna, db_column='upi', to_field='upi', related_name='xrefs')
    version_i = models.IntegerField()
    deleted = models.CharField(max_length=1)
    timestamp = models.DateTimeField()
    userstamp = models.CharField(max_length=100)
    version = models.IntegerField()
    taxid = models.IntegerField()

    class Meta:
        db_table = 'xref'

    def has_modified_nucleotides(self):
        """
        Determine whether an xref has modified nucleotides.
        """
        if self.modifications.count() > 0:
            return True
        else:
            return False

    def get_distinct_modifications(self):
        """
        Get a list of distinct modified nucleotides described in this xref.
        """
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
        class ChemicalComponentSerializer(serializers.ModelSerializer):
            """
            Django Rest Framework serializer class for chemical components.
            """
            id = serializers.CharField()
            description = serializers.CharField()
            one_letter_code = serializers.CharField()
            ccd_id = serializers.CharField()
            source = serializers.CharField()
            modomics_short_name = serializers.CharField()
            pdb_url = serializers.Field(source='get_pdb_url')
            modomics_url = serializers.Field(source='get_modomics_url')

            class Meta:
                model = ChemicalComponent

        class ModificationSerializer(serializers.ModelSerializer):
            """
            Django Rest Framework serializer class for modified positions.
            """
            position = serializers.IntegerField()
            author_assigned_position = serializers.IntegerField()
            chem_comp = ChemicalComponentSerializer(source='modification_id')

            class Meta:
                model = Modification

        serializer = ModificationSerializer(self.modifications.all(), many=True)
        return JSONRenderer().render(serializer.data)

    def is_active(self):
        """
        Convenience method for determining whether
        an xref is current or obsolete.
        """
        if self.deleted == 'N':
            return True
        else:
            return False

    def is_rfam_seed(self):
        """
        Determine whether an xref is part of a manually curated
        RFAM seed alignment.
        """
        if re.search('alignment\:seed', self.accession.note, re.IGNORECASE) is not None:
            return True
        else:
            return False

    def get_ncbi_gene_id(self):
        """
        GeneID links are stored in the db_xref field.
        """
        match = re.search('GeneID\:(\d+)', self.accession.db_xref, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            return None

    def get_ndb_external_url(self):
        """
        For some entries NDB uses different ids than those assigned by the PDB.
        NDB ids are store in the db_xref column.
        This function returns an NDB url using NDB ids where possible
        with PDB ids used as a fallback.
        """
        ndb_url = 'http://ndbserver.rutgers.edu/service/ndb/atlas/summary?searchTarget={structure_id}'
        match = re.search('NDB\:(\w+)', self.accession.db_xref, re.IGNORECASE)
        if match:
            structure_id = match.group(1) # NDB id
        else:
            structure_id = self.accession.external_id # default to PDB id
        return ndb_url.format(structure_id=structure_id)

    def get_ucsc_bed(self):
        """
        Format genomic coordinates in BED format.
        """
        return _xref_to_bed_format(self)

    def get_gff(self):
        """
        Format genomic coordinates in GFF format.
        """
        return GffFormatter(self)()

    def get_gff3(self):
        """
        Format genomic coordinates in GFF3 format.
        """
        return Gff3Formatter(self)()

    def is_mirbase_mirna_precursor(self):
        """
        True if the accession is a miRBase precursor miRNA.
        """
        if self.accession.feature_name == 'precursor_RNA' and \
           self.accession.database == 'MIRBASE':
            return True
        else:
            return False

    def get_mirbase_mature_products(self):
        """
        miRBase mature products and precursors share
        the same external MI* identifier.
        """
        mature_products = Xref.objects.filter(accession__external_id=self.accession.external_id,
                                              accession__feature_name='ncRNA').\
                                       all()
        upis = []
        for mature_product in mature_products:
            upis.append(mature_product.upi)
        return upis

    def get_mirbase_precursor(self):
        """
        miRBase mature products and precursors share
        the same external MI* identifier.
        """
        precursor = Xref.objects.filter(accession__external_id=self.accession.external_id,
                                        accession__feature_name='precursor_RNA').\
                                 first()
        if precursor:
            return precursor.upi.upi
        else:
            return None

    def is_refseq_mirna(self):
        """
        RefSeq miRNAs are stored in 3 xrefs:
            * precursor_RNA
            * 5-prime ncRNA
            * 3-prime ncRNA
        which share the same parent accession.
        """
        same_parent = Xref.objects.filter(accession__parent_ac=self.accession.parent_ac,
                                          accession__ncrna_class='miRNA',
                                          deleted=self.deleted).\
                                   all()
        if len(same_parent) > 1:
            return True
        else:
            return False

    def get_refseq_mirna_precursor(self):
        """
        Given a 5-prime or 3-prime mature product, retrieve its precursor miRNA.
        """
        if self.accession.feature_name != 'precursor_RNA':
            rna = Xref.objects.filter(accession__parent_ac=self.accession.parent_ac,
                                      accession__feature_name='precursor_RNA').\
                               first()
            if rna:
                return rna.upi
        return None

    def get_refseq_mirna_mature_products(self):
        """
        Given a precursor miRNA, retrieve its mature products.
        """
        mature_products = Xref.objects.filter(accession__parent_ac=self.accession.parent_ac,
                                              accession__feature_name='ncRNA').\
                                       all()
        upis = []
        for mature_product in mature_products:
            upis.append(mature_product.upi)
        return upis

    def get_refseq_splice_variants(self):
        """
        RefSeq splice variants are identified by the same GeneID.
        Example: URS000075D687.
        """
        splice_variants = []
        gene_id = self.get_ncbi_gene_id()
        if gene_id:
            xrefs = Xref.objects.filter(db__display_name='RefSeq',
                                        deleted='N',
                                        accession__ncrna_class=self.accession.ncrna_class,
                                        accession__db_xref__iregex='GeneId:'+gene_id).\
                                 exclude(accession=self.accession.accession).\
                                 all()
            for splice_variant in xrefs:
                splice_variants.append(splice_variant.upi)
            splice_variants.sort(key=lambda x: x.length)
        return splice_variants

    def get_vega_splice_variants(self):
        """
        Alternative transcripts are grouped by the same Gene id.
        Vega gene names are stored in optional_id while
        transcript names are stored in external_id.
        """
        splice_variants = []
        if not re.match('vega', self.db.display_name, re.IGNORECASE):
            return splice_variants
        for splice_variant in Accession.objects.filter(optional_id=self.accession.optional_id).\
                                                exclude(accession=self.accession.accession).\
                                                all():
            for splice_xref in splice_variant.xrefs.all():
                if splice_xref.deleted == 'N':
                    splice_variants.append(splice_xref.upi)
            splice_variants.sort(key=lambda x: x.length)
        return splice_variants

    def get_tmrna_mate_upi(self):
        """
        Get the mate of the 2-piece tmRNA
        """
        if self.db.display_name != 'tmRNA Website':
            tmrna_mate_upi = False
        if not self.accession.optional_id:  # no mate info
            tmrna_mate_upi = False
        mate = Accession.objects.filter(parent_ac=self.accession.optional_id, is_composite='Y').get()
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
            tmrna_type = 0 # not tmRNA
        if not self.accession.optional_id:
            tmrna_type = 1 # one-piece or precursor
        else:
            tmrna_type = 2 # two-piece tmRNA
        return tmrna_type

    def get_ensembl_species_name(self):
        """
        Get a species name that can be used in Ensembl urls.
        """
        if self.accession.species == 'Dictyostelium discoideum AX4':
            self.accession.species = 'Dictyostelium discoideum'
        return self.accession.species.replace(' ', '_').lower()

    def get_ensembl_division(self):
        """
        Get Ensembl or Ensembl Genomes division for the cross-reference.
        """
        species = self.get_ensembl_species_name()
        species = species.replace('_', ' ').capitalize()

        ensembl_divisions = get_ensembl_divisions()
        for division in ensembl_divisions:
            if species in [x['name'] for x in division['species']]:
                return division
        return { # fall back to ensembl.org
            'name': 'Ensembl',
            'url': 'http://ensembl.org',
        }

    def get_ucsc_db_id(self):
        """
        Get UCSC id for the genome assembly.
        http://genome.ucsc.edu/FAQ/FAQreleases.html
        """
        for genome in rnacentral_genomes:
            if self.taxid == genome['taxid']:
                return genome['assembly_ucsc']
        return None

    def has_genomic_coordinates(self):
        """
        Determine whether an xref has genomic coordinates.
        """
        chromosomes = self.accession.coordinates.values_list('chromosome', flat=True)
        for chromosome in chromosomes:
            if chromosome:
                return True
        return False

    def get_genomic_coordinates(self):
        """
        Mirror the existing API while using the new GenomicCoordinates model.
        """
        data = {
            'chromosome': self.get_feature_chromosome(),
            'strand': self.get_feature_strand(),
            'start': self.get_feature_start(),
            'end': self.get_feature_end(),
        }
        exceptions = ['X', 'Y']
        if re.match(r'\d+', data['chromosome']) or data['chromosome'] in exceptions:
            data['ucsc_chromosome'] = 'chr' + data['chromosome']
        else:
            data['ucsc_chromosome'] = data['chromosome']
        return data

    def get_feature_chromosome(self):
        """
        Get the chromosome name for the genomic location.
        The name represents a toplevel accession as defined
        by the Ensembl API and can include patch/scaffold names etc.
        """
        return GenomicCoordinates.objects.\
                                  filter(accession=self.accession.accession,
                                         chromosome__isnull=False).\
                                  first().\
                                  chromosome

    def get_feature_strand(self):
        """
        Return 1 or -1 to indicate the forward and reverse strands respectively.
        """
        return GenomicCoordinates.objects.\
                                  filter(accession=self.accession.accession,
                                         chromosome__isnull=False, ).\
                                  first().\
                                  strand

    def get_feature_start(self):
        """
        Get the `start` coordinates of the genomic feature.
        """
        data = self.accession.coordinates.aggregate(min_feature_start = Min('primary_start'))
        return data['min_feature_start']

    def get_feature_end(self):
        """
        Get the `end` coordinates of the genomic feature.
        """
        data = self.accession.coordinates.aggregate(max_feature_end = Max('primary_end'))
        return data['max_feature_end']


class Reference(models.Model):
    authors = models.TextField()
    location = models.CharField(max_length=4000)
    title = models.CharField(max_length=4000)
    pubmed = models.CharField(max_length=10, db_column='pmid')
    doi = models.CharField(max_length=80)

    def get_title(self):
        title = self.title
        if self.location[:9] == 'Submitted':
            title = 'INSDC submission'
        else:
            title = title if title else 'No title available'
        return title

    def get_authors_list(self):
        """
        Get publication authors as a list.
        """
        if self.authors:
            return self.authors.split(', ')
        else:
            return []

    class Meta:
        db_table = 'rnc_references'


class Reference_map(models.Model):
    accession = models.ForeignKey(Accession, db_column='accession', to_field='accession', related_name='refs')
    data = models.ForeignKey(Reference, db_column='reference_id')

    class Meta:
        db_table = 'rnc_reference_map'

"""
Common auxiliary functions.
"""
class Gff3Formatter(object):
    """
    GFF3 format documentation:
    http://www.sequenceontology.org/gff3.shtml
    http://gmod.org/wiki/GFF3#GFF3_Format
    """
    def __init__(self, xref):
        """
        Take Xref object instance as an argument.
        """
        self.xref = xref
        self.gff = ''
        self.exons = None
        fields = ['seqid', 'source', 'seq_type', 'chrom_start',
                  'chrom_end', 'score', 'strand', 'phase', 'attributes']
        self.template =  '\t'.join(['{' + x + '}' for x in fields])  + '\n'

    def get_exons(self):
        """
        Get all exons with genome mapping
        that are associated with a cross-reference.
        """
        accession = self.xref.accession.accession
        self.exons = GenomicCoordinates.objects.\
                                        filter(accession=accession,
                                               chromosome__isnull=False).\
                                        all()

    def format_attributes(self, attributes, order):
        """
        Format the `attributes` field.
        """
        return ';'.join("%s=%s" % (key, attributes[key]) for key in order)

    def format_transcript(self):
        """
        Format transcipt description.
        Transcipt ID is the Parent of exons.
        """
        attributes = {
            'ID': self.xref.accession.accession,
            'Name': self.xref.upi.upi,
            'type': self.xref.accession.get_rna_type(),
        }
        order = ['ID', 'Name', 'type']
        data = {
            'seqid': self.xref.get_feature_chromosome(),
            'source': 'RNAcentral',
            'seq_type': 'transcript',
            'chrom_start': self.xref.get_feature_start(),
            'chrom_end': self.xref.get_feature_end(),
            'score': '.',
            'phase': '.',
            'strand': '+' if self.xref.get_feature_strand() > 0 else '-',
            'attributes': self.format_attributes(attributes, order),
        }
        self.gff += self.template.format(**data)

    def format_exons(self):
        """
        Format a list of non-coding exons.
        Transcipt ID is the Parent of exons.
        """
        for i, exon in enumerate(self.exons):
            if not exon.chromosome:
                continue
            attributes = {
                'ID': '_'.join([self.xref.accession.accession, 'exon' + str(i+1)]),
                'Name': self.xref.upi.upi,
                'Parent': self.xref.accession.accession,
                'type': self.xref.accession.get_rna_type(),
            }
            order = ['ID', 'Name', 'Parent', 'type']
            data = {
                'seqid': exon.chromosome,
                'source': 'RNAcentral',
                'seq_type': 'noncoding_exon',
                'chrom_start': exon.primary_start,
                'chrom_end': exon.primary_end,
                'score': '.',
                'phase': '.',
                'strand': '+' if exon.strand > 0 else '-',
                'attributes': self.format_attributes(attributes, order),
            }
            self.gff += self.template.format(**data)

    def consistent_strands(self):
        """
        Check that all exons are mapped to the same strand.
        There was a problem with genomic mapping of short exons
        that could be placed on a wrong strand.
        Example: URS000075A653 (NR_110790.1:1..1533:ncRNA)
        """
        strand = self.exons[0].strand
        for exon in self.exons:
            if exon.strand != strand:
                return False
        return True

    def __call__(self):
        """
        Main entry point for the class.
        """
        # skip TPAs to avoid duplication with the corresponding ENA records
        if self.xref.accession.non_coding_id:
            return self.gff
        self.get_exons()
        if self.exons.count() == 0:
            return self.gff
        # skip the whole transcript if the strands are inconsistent
        if not self.consistent_strands():
            return self.gff
        self.format_transcript()
        self.format_exons()
        return self.gff


class GffFormatter(Gff3Formatter):
    """
    GFF format documentation:
    https://www.sanger.ac.uk/resources/software/gff/spec.html
    Use the same logic as in GFF3
    but format the attributes field differently.
    """
    def format_attributes(self, attributes, order):
        """
        Format the `attributes` field.
        """
        return ';'.join('%s "%s"' % (key, attributes[key]) for key in order)


def _xref_to_bed_format(xref):
    """
    Return genome coordinates of an xref in BED format. Available in Rna and Xref models.
    """
    bed = ''
    exons_all = xref.accession.coordinates.order_by('primary_start').all()
    exons = []
    for exon in exons_all:
        if exon.chromosome:
            exons.append(exon)
        else:
            return bed  # skip entries with unmapped exons
    if len(exons) == 0:
        return bed
    # prepare fields
    chromosome = xref.get_feature_chromosome()
    chrom_start = xref.get_feature_start()
    chrom_end = xref.get_feature_end()
    upi = xref.upi.upi
    score = 0
    strand = '+' if xref.get_feature_strand() > 0 else '-'
    thick_start = chrom_start
    thick_end = chrom_end
    item_rgb = "63,125,151"
    block_count = len(exons)
    block_sizes = []
    block_starts = []
    for i, exon in enumerate(exons):
        block_sizes.append(exon.primary_end - exon.primary_start or 1) # equals 1 if start == end
        if i == 0:
            block_starts.append(0)
        else:
            block_starts.append(exon.primary_start - exons[0].primary_start)
    bed = "%s\t%i\t%i\t%s\t%i\t%s\t%i\t%i\t%s\t%i\t%s\t%s\n" % (chromosome,
                                                                chrom_start,
                                                                chrom_end,
                                                                upi,
                                                                score,
                                                                strand,
                                                                thick_start,
                                                                thick_end,
                                                                item_rgb,
                                                                block_count,
                                                                ','.join(map(str,block_sizes)),
                                                                ','.join(map(str,block_starts))
                                                                )
    return bed

def get_ensembl_divisions():
    """
    A list of species with genomic coordinates grouped by Ensembl division.
    Used for creating links to Ensembl sites.
    """
    return [
        {
            'url': 'http://ensembl.org',
            'name': 'Ensembl',
            'species': [
                {
                    'name': 'Homo sapiens',
                    'taxid': 9606,
                },
                {
                    'name': 'Mus musculus',
                    'taxid': 10090,

                },
                {
                    'name': 'Bos taurus',
                    'taxid': 9913,

                },
                {
                    'name': 'Rattus norvegicus',
                    'taxid': 10116,

                },
                {
                    'name': 'Felis catus',
                    'taxid': 9685,

                },
                {
                    'name': 'Danio rerio',
                    'taxid': 7955,

                },
                {
                    'name': 'Macaca mulatta',
                    'taxid': 9544,

                },
                {
                    'name': 'Pan troglodytes',
                    'taxid': 9598,

                },
                {
                    'name': 'Canis lupus familiaris',
                    'taxid': 9615,

                },
            ],
        },
        {
            'url': 'http://fungi.ensembl.org',
            'name': 'Ensembl Fungi',
            'species': [
                {
                    'name': 'Saccharomyces cerevisiae',
                    'taxid': 4932,
                },
                {
                    'name': 'Schizosaccharomyces pombe',
                    'taxid': 4896,
                },
            ],
        },
        {
            'url': 'http://metazoa.ensembl.org',
            'name': 'Ensembl Metazoa',
            'species': [
                {
                    'name': 'Caenorhabditis elegans',
                    'taxid': 6239,
                },
                {
                    'name': 'Drosophila melanogaster',
                    'taxid': 7227,
                },
                {
                    'name': 'Bombyx mori',
                    'taxid': 7091,
                },
                {
                    'name': 'Anopheles gambiae',
                    'taxid': 7165,
                },
            ],
        },
        {
            'url': 'http://protists.ensembl.org',
            'name': 'Ensembl Protists',
            'species': [
                {
                    'name': 'Dictyostelium discoideum',
                    'taxid': 44689,
                },
                {
                    'name': 'Plasmodium falciparum',
                    'taxid': 5833,
                },
            ],
        },
        {
            'url': 'http://plants.ensembl.org',
            'name': 'Ensembl Plants',
            'species': [
                {
                    'name': 'Arabidopsis thaliana',
                    'taxid': 3702,
                }
            ],
        },
        {
            'url': 'http://bacteria.ensembl.org',
            'name': 'Ensembl Bacteria',
            'species': [],
        },
    ]
