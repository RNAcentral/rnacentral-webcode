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

import re
from xml.sax import saxutils
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
                   t2.ncrna_class, t2.product, t2.common_name, t2.note,
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
                  t1.upi = :upi AND
                  t1.taxid = :taxid
            """
            self.cursor.prepare(sql)

        self.data = dict()

        # fields with redundant values; for example, a single sequence
        # can be associated with multiple taxids.
        # these strings must match the SQL query return values
        # and will become keys in self.data
        self.redundant_fields = ['taxid', 'species', 'expert_db', 'organelle',
                                 'created', 'last', 'deleted', 'description',
                                 'function', 'gene', 'gene_synonym', 'note',
                                 'product', 'common_name', 'parent_accession',]
        # other data fields for which the sets should be (re-)created
        self.data_fields = ['rna_type', 'authors', 'journal', 'popular_species',
                            'pub_title', 'pub_id', 'insdc_submission', 'xrefs',]

        self.popular_species = set([
            9606,   # human
            10090,  # mouse
            7955,   # zebrafish
            3702,   # Arabidopsis thaliana
            6239,   # Caenorhabditis elegans
            7227,   # Drosophila melanogaster
            559292, # Saccharomyces cerevisiae S288c
            4896,   # Schizosaccharomyces pombe
            511145, # Escherichia coli str. K-12 substr. MG1655
            224308, # Bacillus subtilis subsp. subtilis str. 168
        ])

        self.reset()
        self.get_connection()
        self.get_cursor()
        prepare_sql_statement()

    def reset(self):
        """
        Initialize or reset self.data so that the same object can be reused
        for different sequences.
        """
        self.data = {
            'upi': None,
            'md5': None,
            'boost': None,
            'length': 0,
        }

        # (re-)create sets for all data fields
        for field in self.redundant_fields + self.data_fields:
            self.data[field] = set()

    def retrieve_data_from_database(self, upi, taxid):
        """
        Some data is retrieved directly from the database because
        django ORM creates too much overhead.
        """

        def store_redundant_fields():
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

        def store_xrefs():
            """
            Store xrefs as (database, accession) tuples in self.data['xrefs'].
            """
            # expert_db should not contain spaces, EBeye requirement
            result['expert_db'] = result['expert_db'].replace(' ','_').upper()
            # an expert_db entry
            if result['non_coding_id'] or result['expert_db']:
                self.data['xrefs'].add((result['expert_db'],
                                        result['external_id']))
            else: # source ENA entry
                # Non-coding entry
                expert_db = 'NON-CODING' # EBeye requirement
                self.data['xrefs'].add((expert_db, result['accession']))
            # parent ENA entry
            # except for PDB entries which are not based on ENA accessions
            if result['expert_db'] != 'PDBE':
                self.data['xrefs'].add(('ENA', result['parent_accession']))
            if result['note']:
                # extract GO terms from `note`
                for go_term in re.findall('GO\:\d+', result['note']):
                    self.data['xrefs'].add(('GO', go_term))
                # extract SO terms from `note`
                for so_term in re.findall('SO\:\d+', result['note']):
                    self.data['xrefs'].add(('SO', so_term))
                # extract ECO terms from `note`
                for eco_term in re.findall('ECO\:\d+', result['note']):
                    self.data['xrefs'].add(('ECO', eco_term))

        def store_rna_type():
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

        self.cursor.execute(None, {'upi': upi, 'taxid': taxid})
        for row in self.cursor:
            result = self.row_to_dict(row)
            store_redundant_fields()
            store_xrefs()
            store_rna_type()

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

        def count(source):
            """
            Convenience method for finding the number of distinct taxids, expert_dbs
            and other arrays from self.data.
            Example:
            count('taxid')
            """
            if source in self.data:
                return len(self.data[source])
            else:
                return None

        num_descriptions = count('description')
        if num_descriptions == 1:
            description_line = next(iter(self.data['description']))
            description_line = description_line[0].upper() + description_line[1:]
        else:
            if count('product') == 1:
                rna_type = next(iter(self.data['product']))
            elif count('gene') == 1:
                rna_type = next(iter(self.data['gene']))
            else:
                rna_type = '/'.join(self.data['rna_type'])

            distinct_species = count('species')
            if distinct_species == 1:
                species = next(iter(self.data['species']))
                description_line = '{species} {rna_type}'.format(
                                    species=species, rna_type=rna_type)
            else:
                description_line = ('{rna_type} from '
                                    '{distinct_species} species').format(
                                    rna_type=rna_type,
                                    distinct_species=distinct_species)
        return description_line

    def store_literature_references(self, rna, taxid):
        """
        Store literature reference data.
        """

        def process_location(location):
            """
            Store the location field either as journal or INSDC submission.
            """
            if re.match('^Submitted', location):
                location = re.sub('Submitted \(\d{2}\-\w{3}\-\d{4}\) to the INSDC\. ?', '', location)
                if location:
                    self.data['insdc_submission'].add(location)
            else:
                if location:
                    self.data['journal'].add(location)

        for ref in rna.get_publications(taxid=taxid):
            self.data['pub_id'].add(ref.id)
            if ref.authors:
                self.data['authors'].add(ref.authors)
            if ref.title:
                self.data['pub_title'].add(saxutils.escape(ref.title))
            if ref.pubmed:
                self.data['xrefs'].add(('PUBMED', ref.pubmed))
            if ref.doi:
                self.data['xrefs'].add(('DOI', ref.doi))
            if ref.location:
                process_location(saxutils.escape(ref.location))

    def store_popular_species(self):
        """
        Get a subset of all species that are thought to be most popular.
        The data are used to create the Popular species facet.
        """
        self.data['popular_species'] = self.data['taxid'] & self.popular_species # intersection

    def compute_boost_value(self):
        """
        Determine ordering in search results.
        """
        if self.is_active() == 'Active' and 9606 in self.data['taxid']:
            # human entries have max priority
            boost = 3
        elif self.is_active() == 'Active' and self.popular_species & self.data['taxid']:
            # popular species are given priority
            boost = 2
        elif self.is_active() == 'Obsolete':
            # no priority for obsolete entries
            boost = 0
        else:
            # basic priority level
            boost = 1
        self.data['boost'] = boost

    def store_rna_properties(self, rna):
        """
        """
        self.data['upi'] = rna.upi
        self.data['md5'] = rna.md5
        self.data['length'] = rna.length

    def format_xml_entry(self, taxid):
        """
        Format self.data as an xml entry.
        Using Django templates is slower than constructing the entry manually.
        """

        def wrap_in_field_tag(name, value):
            """
            A method for creating field tags.
            """
            try:
                result = '<field name="{0}">{1}</field>'.format(name, value)
            except UnicodeEncodeError:
                value = value.encode('ascii', 'ignore').decode('ascii')
                result = '<field name="{0}">{1}</field>'.format(name, value)
            return result

        def format_field(field):
            """
            Wrap additional fields in <field name=""></field> tags.
            """
            text = []
            for value in self.data[field]:
                if value: # organelle can be empty e.g.
                    text.append(wrap_in_field_tag(field, value))
            return '\n'.join(text)

        def format_cross_references():
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

        def format_author_fields():
            """
            Store authors in separate tags to enable more precise searching.
            """
            authors = set()
            for author_list in self.data['authors']:
                for author in author_list.split(', '):
                    authors.add(author)
            return '\n'.join([wrap_in_field_tag('author', x) for x in authors])

        def format_whitespace(text):
            """
            Strip out useless whitespace.
            """
            text = re.sub('\n\s+\n', '\n', text) # delete empty lines (if gene_synonym is empty e.g. )
            return re.sub('\n +', '\n', text) # delete whitespace at the beginning of lines

        text = """
        <entry id="{upi}_{taxid}">
            <name>Unique RNA Sequence {upi}_{taxid}</name>
            <description>{description}</description>
            <dates>
                <date value="{first_seen}" type="first_seen" />
                <date value="{last_seen}" type="last_seen" />
            </dates>
            <cross_references>
                {cross_references}
            </cross_references>
            <additional_fields>
                {is_active}
                {length}
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
                {md5}
                {authors}
                {journal}
                {insdc_submission}
                {pub_title}
                {pub_id}
                {popular_species}
                {boost}
            </additional_fields>
        </entry>
        """.format(upi=self.data['upi'],
                   description=self.get_description(),
                   first_seen=self.first_seen(),
                   last_seen=self.last_seen(),
                   cross_references=format_cross_references(),
                   is_active=wrap_in_field_tag('active', self.is_active()),
                   length=wrap_in_field_tag('length', self.data['length']),
                   species=format_field('species'),
                   organelles=format_field('organelle'),
                   expert_dbs=format_field('expert_db'),
                   common_name=format_field('common_name'),
                   function=format_field('function'),
                   gene=format_field('gene'),
                   gene_synonym=format_field('gene_synonym'),
                   rna_type=format_field('rna_type'),
                   product=format_field('product'),
                   has_genomic_coordinates=wrap_in_field_tag('has_genomic_coordinates',
                                            str(self.data['has_genomic_coordinates'])),
                   md5=wrap_in_field_tag('md5', self.data['md5']),
                   authors=format_author_fields(),
                   journal=format_field('journal'),
                   insdc_submission = format_field('insdc_submission'),
                   pub_title=format_field('pub_title'),
                   pub_id=format_field('pub_id'),
                   popular_species=format_field('popular_species'),
                   boost=wrap_in_field_tag('boost', self.data['boost']),
                   taxid=taxid)
        return format_whitespace(text)

    ##################
    # Public methods #
    ##################

    def get_xml_entry(self, rna):
        """
        Public method for outputting an xml dump entry for a given UPI.
        """
        taxids = rna.xrefs.values_list('taxid', flat=True).distinct()
        text = ''
        for taxid in taxids:
            self.reset()
            self.store_rna_properties(rna)
            self.data['has_genomic_coordinates'] = rna.has_genomic_coordinates(taxid=taxid)
            self.retrieve_data_from_database(rna.upi, taxid)
            self.store_literature_references(rna, taxid)
            self.store_popular_species()
            self.compute_boost_value()
            text += self.format_xml_entry(taxid)
        return text
