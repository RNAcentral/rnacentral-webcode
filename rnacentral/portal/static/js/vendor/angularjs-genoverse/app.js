// This is an example of an angular application, using angularjs-genoverse

(function() {

angular.module("Example", ["Genoverse"]);

/**
 * Turn on html5mode only in modern browsers because
 * in the older ones html5mode rewrites urls with Hangbangs
 * which break normal Django pages.
 * With html5mode off IE lt 10 will be able to navigate the site
 * but won't be able to open deep links to Angular pages
 * (for example, a link to a search result won't load in IE 9).
 */
angular.module('Example').config(['$locationProvider', function($locationProvider) {
    if (window.history && window.history.pushState) {
        $locationProvider.html5Mode(true);
    }
}]);

angular.module('Example').controller('GenoverseGenomeBrowser', ['$scope', '$location', '$filter', function ($scope, $location, $filter) {
    // Constructor
    // -----------

    $scope.genomes = genomes = [
        // Ensembl
        {
            'species': 'Homo sapiens',
            'synonyms': ['human'],
            'assembly': 'GRCh38',
            'assembly_ucsc': 'hg38',
            'taxid': 9606,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 'X',
                'start': 73792205,
                'end': 73829231
            }
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
                'start': 86351981,
                'end': 86352127
            }
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
                'start': 7633985,
                'end': 7634135
            }
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
                'start': 82197714,
                'end': 82197796
            }
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
                'start': 118277684,
                'end': 118277795
            }
        },
        // {
        //     'species': 'Felis catus',
        //     'synonyms': ['cat'],
        //     'assembly': 'Felis_catus_6.2',
        //     'assembly_ucsc': 'felCat5',
        //     'taxid': 9685,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 'X',
        //         'start': 18058223,
        //         'end': 18058546
        //     }
        // },
        // {
        //     'species': 'Macaca mulatta',
        //     'synonyms': ['macaque'],
        //     'assembly': 'MMUL_1',
        //     'assembly_ucsc': '', # no matching assembly
        //     'taxid': 9544,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 1,
        //         'start': 146238837,
        //         'end': 146238946
        //     }
        // },
        {
            'species': 'Pan troglodytes',
            'synonyms': ['chimp'],
            'assembly': 'CHIMP2.1.4',
            'assembly_ucsc': 'panTro4',
            'taxid': 9598,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 11,
                'start': 78369057,
                'end': 78369163
            }
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
                'start': 22006963,
                'end': 22007066
            }
        },
        // {
        //     'species': 'Gallus gallus',
        //     'synonyms': ['chicken'],
        //     'assembly': 'Galgal4',
        //     'assembly_ucsc': 'galGal4',
        //     'taxid': 9031,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 9,
        //         'start': 15676031,
        //         'end': 15676160
        //     }
        // },
        // {
        //     'species': 'Xenopus tropicalis',
        //     'synonyms': ['frog'],
        //     'assembly': 'JGI_4.2',
        //     'assembly_ucsc': 'xenTro3',
        //     'taxid': 8364,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 'NC_006839',
        //         'start': 11649,
        //         'end': 11717
        //     }
        // },
        // Ensembl Fungi
        // {
        //     'species': 'Saccharomyces cerevisiae',
        //     'synonyms': ['budding yeast', 'Saccharomyces cerevisiae S288c'],
        //     'assembly': 'R64-1-1',
        //     'assembly_ucsc': '',
        //     'taxid': 559292,
        //     'division': 'Ensembl Fungi',
        //     'example_location': {
        //         'chromosome': 'XII',
        //         'start': 856709,
        //         'end': 856919
        //     }
        // },
        {
            'species': 'Schizosaccharomyces pombe',
            'synonyms': ['fission yeast'],
            'assembly': 'ASM294v2',
            'assembly_ucsc': '',
            'taxid': 4896,
            'division': 'Ensembl Fungi',
            'example_location': {
                'chromosome': 'I',
                'start': 541795,
                'end': 543483
            }
        },
        // Ensembl Metazoa
        {
            'species': 'Caenorhabditis elegans',
            'synonyms': ['worm'],
            'assembly': 'WBcel235',
            'assembly_ucsc': '',
            'taxid': 6239,
            'division': 'Ensembl Metazoa',
            'example_location': {
                'chromosome': 'III',
                'start': 11467449,
                'end': 11467620
            }
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
                'start': 7474553,
                'end': 7474996
            }
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
                'start': 6180119,
                'end': 6180321
            }
        },
        // {
        //     'species': 'Anopheles gambiae',
        //     'synonyms': [],
        //     'assembly': 'AgamP4',
        //     'assembly_ucsc': '',
        //     'taxid': 7165,
        //     'division': 'Ensembl Metazoa',
        //     'example_location': {
        //         'chromosome': '2R',
        //         'start': 34644956,
        //         'end': 34645131
        //     }
        // },
        // Ensembl Protists
        {
            'species': 'Dictyostelium discoideum',
            'synonyms': [],
            'assembly': 'dictybase.01',
            'assembly_ucsc': '',
            'taxid': 44689,
            'division': 'Ensembl Protists',
            'example_location': {
                'chromosome': 2,
                'start': 7876933,
                'end': 7877055
            }
        },
        // {
        //     'species': 'Plasmodium falciparum',
        //     'synonyms': [],
        //     'assembly': 'ASM276v1',
        //     'assembly_ucsc': '',
        //     'taxid': 5833,
        //     'division': 'Ensembl Protists',
        //     'example_location': {
        //         'chromosome': 13,
        //         'start': 2796339,
        //         'end': 2798488
        //     }
        // },
        // Ensembl Plants
        {
            'species': 'Arabidopsis thaliana',
            'synonyms': [],
            'assembly': 'TAIR10',
            'assembly_ucsc': '',
            'taxid': 3702,
            'division': 'Ensembl Plants',
            'example_location': {
                'chromosome': 2,
                'start': 18820691,
                'end': 18822184
            }
        }
    ];

    // from JS standpoint, genome and genomes[i] == genome are different objects, but we want exactly the same, so:
    $scope.genome = genomes[0];

    $scope.chromosome = "X";
    $scope.start = 73792205;
    $scope.end = 73829231;

    // reflect any changes in genome in address bar
    $scope.$watch('genome', setUrl);
    $scope.$watch('chromosome', setUrl);
    $scope.$watch('start', setUrl);
    $scope.$watch('stop', setUrl);

    // Method definitions
    // ------------------

    /**
     * Sets the url in address bar to reflect the changes in browser location
     */
    function setUrl(newValue, oldValue) {
        // set the full url
        $location.path("/" + $filter('urlencodeSpecies')($scope.genome.species)); // this filter's from Genoverse module
        $location.search({chromosome: $scope.chromosome, start: $scope.start, end: $scope.end});
        $location.replace();
    }

}]);

})();
