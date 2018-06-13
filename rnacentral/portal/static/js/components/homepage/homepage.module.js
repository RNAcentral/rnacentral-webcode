var HomepageController = function($scope) {
    $scope.rainbowTroutPublication = {
        "title": "Genome-Wide Discovery of Long Non-Coding RNAs in Rainbow Trout.",
        "authors": ["Al-Tobasei R", "Paneru B", "Salem M"],
        "publication": "PLoS One. 2016 Feb 19;11(2):e0148940",
        "pubmed_id": 26895175,
        "doi": "10.1371/journal.pone.0148940",
        "pub_id": ""
    };

    $scope.bovineLeukemiaPublication = {
        "title": "Characterization of novel Bovine Leukemia Virus (BLV) antisense transcripts by deep sequencing reveals constitutive expression in tumors and transcriptional interaction with viral microRNAs.",
        "authors": ["Durkin K", "Rosewick N", "Artesi M", "Hahaut V", "Griebel P", "Arsic N", "Burny A", "Georges M", "Van den Broeke A"],
        "publication": "Retrovirology. 2016 May 3;13(1):33",
        "pubmed_id": 27141823,
        "doi": "10.1186/s12977-016-0267-8",
        "pub_id": ""
    };

    $scope.goCurationPublication = {
        "title": "Guidelines for the functional annotation of microRNAs using the Gene Ontology.",
        "authors": ["Huntley RP", "Sitnikov D", "Orlic-Milacic M", "Balakrishnan R", "D'Eustachio P", "Gillespie ME", "Howe D", "Kalea AZ", "Maegdefessel L", "Osumi-Sutherland D", "Petri V", "Smith JR", "Van Auken K", "Wood V", "Zampetaki A", "Mayr M", "Lovering RC"],
        "publication": "RNA. 2016 May;22(5):667-76",
        "pubmed_id": 26917558,
        "doi": "10.1261/rna.055301.115",
        "pub_id": ""
    };

    $scope.secondaryStructurePredictionPublication = {
        "title": "Forna (force-directed RNA): Simple and effective online RNA secondary structure diagrams.",
        "authors": ["Kerpedjiev P", "Hammer S", "Hofacker IL"],
        "publication": "Bioinformatics. 2015 Oct 15;31(20):3377-9",
        "pubmed_id": 26099263,
        "doi": "doi: 10.1093/bioinformatics/btv372",
        "pub_id": ""
    };
};

HomepageController.$inject = ['$scope'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
