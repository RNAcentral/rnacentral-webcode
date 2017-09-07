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
Common auxiliary functions.
"""
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