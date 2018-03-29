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

"""
Supported genomes.
"""
genomes = [
    # Ensembl
    {
        'species': 'Homo sapiens',
        'synonyms': ['human'],
        'assembly': 'GRCh38',
        'assembly_ucsc': 'hg38',
        'taxid': 9606,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 'X',
            'start': 73819307,
            'end': 73856333,
        },
    },
    {
        'species': 'Mus musculus',
        'synonyms': ['mouse'],
        'assembly': 'GRCm38',
        'assembly_ucsc': 'mm10',
        'taxid': 10090,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 1,
            'start': 86351908,
            'end': 86352200,
        },
    },
    {
        'species': 'Danio rerio',
        'synonyms': ['zebrafish'],
        'assembly': 'GRCz10',
        'assembly_ucsc': 'danRer10',
        'taxid': 7955,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 9,
            'start': 7633910,
            'end': 7634210,
        },
    },
    {
        'species': 'Bos taurus',
        'synonyms': ['cow'],
        'assembly': 'UMD3.1',
        'assembly_ucsc': 'bosTau6',
        'taxid': 9913,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 15,
            'start': 82197673,
            'end': 82197837,
        },
    },
    {
        'species': 'Rattus norvegicus',
        'synonyms': ['rat'],
        'assembly': 'Rnor_6.0',
        'assembly_ucsc': 'rn6',
        'taxid': 10116,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 'X',
            'start': 118277628,
            'end': 118277850,
        },
    },
    # {
    #     'species': 'Felis catus',
    #     'synonyms': ['cat'],
    #     'assembly': 'Felis_catus_6.2',
    #     'assembly_ucsc': 'felCat5',
    #     'taxid': 9685,
    #     'division': 'Ensembl',
    #     'example_location': {
    #         'chromosome': 'X',
    #         'start': 18058223,
    #         'end': 18058546,
    #     },
    # },
    # {
    #     'species': 'Macaca mulatta',
    #     'synonyms': ['macaque'],
    #     'assembly': 'MMUL_1',
    #     'assembly_ucsc': '', # no matching assembly
    #     'taxid': 9544,
    #     'division': 'Ensembl',
    #     'example_location': {
    #         'chromosome': 1,
    #         'start': 146238837,
    #         'end': 146238946,
    #     },
    # },
    {
        'species': 'Pan troglodytes',
        'synonyms': ['chimp'],
        'assembly': 'CHIMP2.1.4',
        'assembly_ucsc': 'panTro4',
        'taxid': 9598,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 11,
            'start': 78369004,
            'end': 78369219,
        },
    },
    {
        'species': 'Canis familiaris',
        'synonyms': ['dog', 'Canis lupus familiaris'],
        'assembly': 'CanFam3.1',
        'assembly_ucsc': 'canFam3',
        'taxid': 9615,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 19,
            'start': 22006909,
            'end': 22007119,
        },
    },
    # {
    #     'species': 'Gallus gallus',
    #     'synonyms': ['chicken'],
    #     'assembly': 'Galgal4',
    #     'assembly_ucsc': 'galGal4',
    #     'taxid': 9031,
    #     'division': 'Ensembl',
    #     'example_location': {
    #         'chromosome': 9,
    #         'start': 15676031,
    #         'end': 15676160,
    #     },
    # },
    # {
    #     'species': 'Xenopus tropicalis',
    #     'synonyms': ['frog'],
    #     'assembly': 'JGI_4.2',
    #     'assembly_ucsc': 'xenTro3',
    #     'taxid': 8364,
    #     'division': 'Ensembl',
    #     'example_location': {
    #         'chromosome': 'NC_006839',
    #         'start': 11649,
    #         'end': 11717,
    #     },
    # },
    # Ensembl Fungi
    # {
    #     'species': 'Saccharomyces cerevisiae',
    #     'synonyms': ['budding yeast', 'Saccharomyces cerevisiae S288c'],
    #     'assembly': 'R64-1-1',
    #     'assembly_ucsc': '',
    #     'taxid': 559292,
    #     'division': 'Ensembl Fungi',
    #     'example_location': {
    #         'chromosome': 'XII',
    #         'start': 856709,
    #         'end': 856919,
    #     },
    # },
    {
        'species': 'Schizosaccharomyces pombe',
        'synonyms': ['fission yeast'],
        'assembly': 'ASM294v2',
        'assembly_ucsc': '',
        'taxid': 4896,
        'division': 'Ensembl Fungi',
        'example_location': {
            'chromosome': 'I',
            'start': 540951,
            'end': 544327,
        },
    },
    # Ensembl Metazoa
    {
        'species': 'Caenorhabditis elegans',
        'synonyms': ['worm'],
        'assembly': 'WBcel235',
        'assembly_ucsc': '',
        'taxid': 6239,
        'division': 'Ensembl Metazoa',
        'example_location': {
            'chromosome': 'III',
            'start': 11467363,
            'end': 11467705,
        },
    },
    {
        'species': 'Drosophila melanogaster',
        'synonyms': ['fly'],
        'assembly': 'BDGP6',
        'assembly_ucsc': 'dm6',
        'taxid': 7227,
        'division': 'Ensembl Metazoa',
        'example_location': {
            'chromosome': '3R',
            'start': 7474331,
            'end': 7475217,
        },
    },
    {
        'species': 'Bombyx mori',
        'synonyms': ['silkworm'],
        'assembly': 'GCA_000151625.1',
        'assembly_ucsc': '',
        'taxid': 7091,
        'division': 'Ensembl Metazoa',
        'example_location': {
            'chromosome': 'scaf16',
            'start': 6180018,
            'end': 6180422,
        },
    },
    # {
    #     'species': 'Anopheles gambiae',
    #     'synonyms': [],
    #     'assembly': 'AgamP4',
    #     'assembly_ucsc': '',
    #     'taxid': 7165,
    #     'division': 'Ensembl Metazoa',
    #     'example_location': {
    #         'chromosome': '2R',
    #         'start': 34644956,
    #         'end': 34645131,
    #     },
    # },
    # Ensembl Protists
    {
        'species': 'Dictyostelium discoideum',
        'synonyms': [],
        'assembly': 'dictybase.01',
        'assembly_ucsc': '',
        'taxid': 44689,
        'division': 'Ensembl Protists',
        'example_location': {
            'chromosome': 2,
            'start': 7874546,
            'end': 7876498,
        },
    },
    # {
    #     'species': 'Plasmodium falciparum',
    #     'synonyms': [],
    #     'assembly': 'ASM276v1',
    #     'assembly_ucsc': '',
    #     'taxid': 5833,
    #     'division': 'Ensembl Protists',
    #     'example_location': {
    #         'chromosome': 13,
    #         'start': 2796339,
    #         'end': 2798488,
    #     },
    # },
    # Ensembl Plants
    {
        'species': 'Arabidopsis thaliana',
        'synonyms': [],
        'assembly': 'TAIR10',
        'assembly_ucsc': '',
        'taxid': 3702,
        'division': 'Ensembl Plants',
        'example_location': {
            'chromosome': 2,
            'start': 18819643,
            'end': 18822629,
        },
    },
]


def url2db(identifier):
    """
    Converts species name from its representation in url to its database representation.
    :param identifier: Species name as in url, e.g. "canis_familiaris"
    :return: Species name as in database "Canis lupus familiaris"
    """
    # special cases
    if identifier in ('canis_familiaris', 'canis_lupus_familiaris'):
        return "Canis lupus familiaris"
    elif identifier in ('gorilla_gorilla', 'gorilla_gorilla_gorilla'):
        return "Gorilla gorilla gorilla"
    elif identifier in ('ceratotherium_simum', 'ceratotherium_simum_simum'):
        return "Ceratotherium simum simum"
    else:
        return identifier.replace('_', ' ').capitalize()


def db2url(identifier):
    """
    Converts species name from its representation in database to url representation.
    :param identifier: Species name as in url, e.g. "Canis lupus familiaris"
    :return: Species name as in database "canis_familiaris"
    """
    # special cases
    if identifier in ("Canis lupus familiaris", "Canis familiaris"):
        return "canis_familiaris"
    elif identifier in ("Gorilla gorilla gorilla", "Gorilla gorilla"):
        return "gorilla_gorilla"
    elif identifier in ("Ceratotherium simum simum", "Ceratotherium simum"):
        return "ceratotherium_simum"
    else:
        return identifier.replace(' ', '_').lower()


def get_taxonomy_info_by_genome_identifier(identifier):
    """
    Returns a valid taxonomy, given a taxon identifier.

    :param identifier: this is what we receive from django named urlparam
    This is either a scientific name, or synonym or taxId. Note: whitespaces
    in it are replaced with hyphens to avoid having to urlencode them.

    :return: e.g. {
        'species': 'Homo sapiens',
        'synonyms': ['human'],
        'assembly': 'GRCh38',
        'assembly_ucsc': 'hg38',
        'taxid': 9606,
        'division': 'Ensembl',
        'example_location': {
            'chromosome': 'X',
            'start': 73792205,
            'end': 73829231,
        }
    }
    """
    identifier = identifier.replace('_', ' ')  # we transform all underscores back to whitespaces

    for genome in genomes:
        # check, if it's a scientific name or a trivial name
        synonyms = [synonym.lower() for synonym in genome['synonyms']]
        if (identifier.lower() == genome['species'].lower() or
           identifier.lower() in synonyms):
            return genome

        # check, if it's a taxid
        try:
            if int(identifier) == genome['taxid']:
                return genome
        except ValueError:
            pass

    return None  # genome not found


class SpeciesNotInGenomes(Exception):
    pass


def get_taxid_from_species(species):
    try:
        return get_taxonomy_info_by_genome_identifier(species)['taxid']
    except Exception as e:
        raise SpeciesNotInGenomes(species)


def get_ucsc_db_id(taxid):
    """Get UCSC id for the genome assembly. http://genome.ucsc.edu/FAQ/FAQreleases.html"""
    for genome in genomes:
        if taxid == genome['taxid']:
            return genome['assembly_ucsc']
    return None


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


def get_ensembl_division(species):
    """Get Ensembl or Ensembl Genomes division for the cross-reference."""
    ensembl_divisions = get_ensembl_divisions()
    for division in ensembl_divisions:
        if species in [x['name'] for x in division['species']]:
            return {'name': division['name'], 'url': division['url']}
    return {  # fall back to ensembl.org
        'name': 'Ensembl',
        'url': 'http://ensembl.org',
    }


def get_ensembl_species_url(species, accession=""):
    if species == 'Dictyostelium discoideum':
        species = 'Dictyostelium discoideum AX4'
    elif species.startswith('Mus musculus') and accession.startswith('MGP'): # Ensembl mouse strain
            parts = accession.split('_')
            if len(parts) == 3:
                species = 'Mus musculus ' + parts[1]
    species = species.replace(' ', '_').lower()
    return species
