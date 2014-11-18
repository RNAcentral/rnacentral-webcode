"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

from xml.sax import saxutils
from django.template.defaultfilters import pluralize
from portal.management.commands.common_exporters.oracle_connection \
    import OracleConnection


class RnaXmlExporter(OracleConnection):
    """
    A class for outputting data about unique RNA sequences in xml dump format
    used for metadata indexing.
    The same class instance is reused for multiple URS to avoid recreating
    class instances and reuse database connection.
    """

    def __init__(self):
        """
        Connect to the database, prepare the query and set up all variables.
        """
        super(RnaXmlExporter, self).__init__()

        def prepare_sql_statement():
            """
            The SQL query retrieves the data about a single sequence
            in one database request. The query is precompiled
            with a UPI placeholder for better performance.
            """
            sql = """
            SELECT t1.taxid, t1.deleted,
                   t2.species, t2.organelle, t2.external_id,
                   t2.description, t2.non_coding_id, t2.accession,
                   t2.function, t2.gene, t2.gene_synonym, t2.feature_name,
                   t2.ncrna_class, t2.product, t2.common_name,
                   t2.parent_ac || '.' || t2.seq_version as parent_accession,
                   t3.display_name as expert_db,
                   t4.timestamp as created,
                   t5.timestamp as last,
                   t6.len as length
            FROM xref t1, rnc_accessions t2, rnc_database t3, rnc_release t4,
                 rnc_release t5, rna t6
            WHERE t1.ac = t2.accession AND
                  t1.dbid = t3.id AND
                  t1.created = t4.id AND
                  t1.last = t5.id AND
                  t1.upi = t6.upi AND
                  t1.upi = :upi
            """
            self.cursor.prepare(sql)

        self.data = dict()

        # fields with redundant values; for example, a single sequence
        # can be associated with multiple taxids.
        # these strings must match the SQL query return values
        # and will become keys in self.data
        self.redundant_fields = ['taxid', 'species', 'expert_db', 'organelle',
                                 'created', 'last', 'deleted', 'description',
                                 'function', 'gene', 'gene_synonym',
                                 'product', 'common_name', 'parent_accession']
        self.initialize()
        self.get_connection()
        self.get_cursor()
        prepare_sql_statement()

    def initialize(self):
        """
        Initialize or reset self.data so that the same object can be reused
        for different sequences.
        """
        self.data = {
            'upi': None,
            'length': 0,
            'xrefs': set(),
        }
        for field in self.redundant_fields:
            self.data[field] = set()
        # additional data requiring custom treatment
        self.data['rna_type'] = set()

    def reset(self):
        """
        Convenience method for self.initialize().
        """
        self.initialize()

    ####################
    # Accessor methods #
    ####################

    def is_active(self):
        """
        Return 'Active' if a sequence has at least one active cross_reference,
        return 'Obsolete' otherwise.
        """
        if 'N' in self.data['deleted']:
            return 'Active'
        else:
            return 'Obsolete'

    def __first_or_last_seen(self, mode):
        """
        Single method for retrieving first/last release dates.
        """
        if mode not in ['created', 'last']:
            return None
        self.data[mode] = list(self.data[mode]) # sets cannot be sorted
        self.data[mode].sort()
        if mode == 'created':
            value = self.data[mode][0] # first
        elif mode == 'last':
            value = self.data[mode][-1] # last
        return value.strftime('%d %b %Y') # 18 Nov 2014 e.g.

    def first_seen(self):
        """
        Return the earliest release date.
        """
        return self.__first_or_last_seen('created')

    def last_seen(self):
        """
        Return the latest release date.
        """
        return self.__first_or_last_seen('last')

    def get_description(self):
        """
        if one ENA entry
            use its description line
        if more than one ENA entry:
            if from 1 organism:
                {species} {rna_type}
                Example: Homo sapiens tRNA
            if from multiple organisms:
                {rna_type} from {x} species
                Example: tRNA from 10 species
                if multuple rna_types, join them by '/'

        Using product or gene is tricky because the same entity can be
        described in a number of ways, for example one sequence
        has the following clearly redundant products:
        tRNA-Phe, transfer RNA-Phe, tRNA-Phe (GAA), tRNA-Phe-GAA etc
        """
        num_descriptions = len(self.data['description'])

        if num_descriptions == 1:
            description_line = self.data['description'].pop()
            description_line = description_line[0].upper() + description_line[1:]
        else:
            distinct_species = self.count('species')

            if len(self.data['product']) == 1:
                rna_type = self.data['product'].pop()
            elif len(self.data['gene']) == 1:
                rna_type = self.data['gene'].pop()
            else:
                rna_type = '/'.join(self.data['rna_type'])

            if distinct_species == 1:
                species = self.data['species'].pop()
                description_line = '{species} {rna_type}'.format(
                                    species=species, rna_type=rna_type)
            else:
                description_line = ('{rna_type} from '
                                    '{distinct_species} species').format(
                                    rna_type=rna_type,
                                    distinct_species=distinct_species)
        return description_line

    def count(self, source):
        """
        Convenience method for finding the number of distinct taxids, expert_dbs
        and other arrays from self.data.
        Example:
        self.count('taxid')
        """
        if source in self.data:
            return len(self.data[source])
        else:
            return None

    def get_additional_field(self, field):
        """
        Wrap additional fields in <field name=""></field> tags.
        """
        text = []
        for value in self.data[field]:
            if value: # organelle can be empty e.g.
                text.append('<field name="{0}">{1}</field>'.format(field,
                    value))
        return '\n'.join(text)

    def get_cross_references(self):
        """
        Wrap xrefs and taxids in <ref dbname="" dbkey=""/> tags.
        Taxids are stored as cross-references.
        """
        text = []
        for xref in self.data['xrefs']:
            text.append('<ref dbname="{0}" dbkey="{1}" />'.format(*xref))
        for taxid in self.data['taxid']:
            text.append('<ref dbkey="{0}" dbname="ncbi_taxonomy_id" />'.format(taxid))
        return '\n'.join(text)

    #####################
    # Output formatting #
    #####################

    def format_xml_entry(self):
        """
        Format self.data as an xml entry.
        Using Django templates is slower than constructing the entry manually.
        """
        return """
        <entry id="{upi}">
            <name>Unique RNA Sequence {upi}</name>
            <description>{description}</description>
            <dates>
                <date value="{first_seen}" type="first_seen" />
                <date value="{last_seen}" type="last_seen" />
            </dates>
            <cross_references>
                {cross_references}
            </cross_references>
            <additional_fields>
                <field name="active">{is_active}</field>
                <field name="length">{length}</field>
                {species}
                {organelles}
                {expert_dbs}
                {common_name}
                {function}
                {gene}
                {gene_synonym}
                {rna_type}
                {product}
                {has_genomic_coordinates}
            </additional_fields>
        </entry>""".format(upi=self.data['upi'],
                           description=self.get_description(),
                           first_seen=self.first_seen(),
                           last_seen=self.last_seen(),
                           cross_references=self.get_cross_references(),
                           is_active=self.is_active(),
                           length=self.data['length'],
                           species=self.get_additional_field('species'),
                           organelles=self.get_additional_field('organelle'),
                           expert_dbs=self.get_additional_field('expert_db'),
                           common_name=self.get_additional_field('common_name'),
                           function=self.get_additional_field('function'),
                           gene=self.get_additional_field('gene'),
                           gene_synonym=self.get_additional_field('gene_synonym'),
                           rna_type=self.get_additional_field('rna_type'),
                           product=self.get_additional_field('product'),
                           has_genomic_coordinates=self.get_additional_field('has_genomic_coordinates'))

    ##################
    # Public methods #
    ##################

    def get_xml_entry(self, rna):
        """
        Public method for outputting an xml dump entry for a given UPI.
        """

        def store_sets(result):
            """
            Store redundant data in sets in order to get distinct values.
            Escape '&', '<', and '>'.
            """
            escape_fields = ['species', 'description', 'product', 'common_name',
                             'function', 'gene', 'gene_synonym']
            for field in self.redundant_fields:
                if result[field]:
                    if field in escape_fields:
                        result[field] = saxutils.escape(result[field])
                    self.data[field].add(result[field])

        def store_xrefs(result):
            """
            Store xrefs as (database, accession) tuples in self.data['xrefs'].
            Do not store deleted xrefs so that they are not indexed.
            """
            if result['deleted'] == 'Y':
                return
            # expert_db should not contain spaces, EBeye requirement
            result['expert_db'] = result['expert_db'].replace(' ','_').upper()
            # an expert_db entry
            if result['non_coding_id'] or result['expert_db'] in ['RFAM', 'REFSEQ', 'RDP']:
                self.data['xrefs'].add((result['expert_db'],
                                        result['external_id']))
            else: # source ENA entry
                # Non-coding entry
                expert_db = 'NON-CODING' # EBeye requirement
                self.data['xrefs'].add((expert_db, result['accession']))
            # parent ENA entry
            self.data['xrefs'].add(('ENA', result['parent_accession']))

        def store_rna_type(result):
            """
            Store distinct RNA type annotations in a set.
            If an entry is an 'ncRNA' feature, it will have a mandatory field
            'ncrna_class' with useful description.
            If an entry is any other RNA feature, use that feature_name
            as rna_type.
            """
            if result['ncrna_class']:
                rna_type = result['ncrna_class']
            else:
                rna_type = result['feature_name']
            self.data['rna_type'].add(rna_type.replace('_', ' '))

        self.reset()
        self.data['upi'] = rna.upi
        self.data['has_genomic_coordinates'] = (str(rna.has_genomic_coordinates()),)
        self.cursor.execute(None, {'upi': rna.upi})

        for row in self.cursor:
            result = self.row_to_dict(row)
            store_sets(result)
            store_xrefs(result)
            store_rna_type(result)
            self.data['length'] = result['length']
        return self.format_xml_entry()
