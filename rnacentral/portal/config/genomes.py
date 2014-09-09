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

"""
Supported genomes.
"""
genomes = [
    # Ensembl
    {
        'species': 'Homo sapiens',
        'assembly': 'GRCh38',
        'assembly_ucsc': 'hg38',
        'taxid': 9606,
        'division': 'Ensembl',
    },
    {
        'species': 'Mus musculus',
        'assembly': 'GRCm38',
        'assembly_ucsc': 'mm10',
        'taxid': '10090',
        'division': 'Ensembl',
    },
    {
        'species': 'Danio rerio',
        'assembly': 'Zv9',
        'assembly_ucsc': 'danRer7',
        'taxid': 7955,
        'division': 'Ensembl',
    },
    {
        'species': 'Bos taurus',
        'assembly': 'UMD3.1',
        'assembly_ucsc': 'bosTau6',
        'taxid': 9913,
        'division': 'Ensembl',
    },
    {
        'species': 'Rattus norvegicus',
        'assembly': 'Rnor_5.0',
        'assembly_ucsc': 'rn5',
        'taxid': 10116,
        'division': 'Ensembl',
    },
    {
        'species': 'Felis catus',
        'assembly': 'Felis_catus_6.2',
        'assembly_ucsc': 'felCat5',
        'taxid': 9685,
        'division': 'Ensembl',
    },
    {
        'species': 'Macaca mulatta',
        'assembly': 'MMUL_1',
        'assembly_ucsc': '', # no matching assembly
        'taxid': 9544,
        'division': 'Ensembl',
    },
    {
        'species': 'Pan troglodytes',
        'assembly': 'CHIMP2.1.4',
        'assembly_ucsc': 'panTro4',
        'taxid': 9598,
        'division': 'Ensembl',
    },
    {
        'species': 'Canis lupus familiaris',
        'assembly': 'CanFam3.1',
        'assembly_ucsc': 'canFam3',
        'taxid': 9615,
        'division': 'Ensembl',
    },
    # Ensembl Fungi
    {
        'species': 'Saccharomyces cerevisiae',
        'assembly': 'R64-1-1',
        'assembly_ucsc': '',
        'taxid': 4932,
        'division': 'Ensembl Fungi',
    },
    {
        'species': 'Schizosaccharomyces pombe',
        'assembly': 'ASM294v2',
        'assembly_ucsc': '',
        'taxid': 4896,
        'division': 'Ensembl Fungi',
    },
    # Ensembl Metazoa
    {
        'species': 'Caenorhabditis elegans',
        'assembly': 'WBcel235',
        'assembly_ucsc': '',
        'taxid': 6239,
        'division': 'Ensembl Metazoa',
    },
    {
        'species': 'Drosophila melanogaster',
        'assembly': 'BDGP5',
        'assembly_ucsc': '',
        'taxid': 7227,
        'division': 'Ensembl Metazoa',
    },
    {
        'species': 'Bombyx mori',
        'assembly': 'GCA_000151625.1',
        'assembly_ucsc': '',
        'taxid': 7091,
        'division': 'Ensembl Metazoa',
    },
    {
        'species': 'Anopheles gambiae',
        'assembly': 'AgamP4',
        'assembly_ucsc': '',
        'taxid': 7165,
        'division': 'Ensembl Metazoa',
    },
    # Ensembl Protists
    {
        'species': 'Dictyostelium discoideum',
        'assembly': 'dictybase.01',
        'assembly_ucsc': '',
        'taxid': 44689,
        'division': 'Ensembl Protists',
    },
    {
        'species': 'Plasmodium falciparum',
        'assembly': 'ASM276v1',
        'assembly_ucsc': '',
        'taxid': 5833,
        'division': 'Ensembl Protists',
    },
    # Ensembl Plants
    {
        'species': 'Arabidopsis thaliana',
        'assembly': 'TAIR10',
        'assembly_ucsc': '',
        'taxid': 3702,
        'division': 'Ensembl Plants',
    },
]
