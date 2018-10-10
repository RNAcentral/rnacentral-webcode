var useCasesService = function() {
    return {
        lebibiPublication: {
            "title": "leBIBI-QBPP: a set of databases and a webtool for automatic phylogenetic analysis of prokaryotic sequences",
            "authors": ["Flandrois JP", "Perrière G", "Gouy M"],
            "publication": "BMC Bioinformatics. 2015 Aug 12;16:251",
            "pubmed_id": 26264559,
            "doi": "10.1186/s12859-015-0692-z",
            "pub_id": "",
            "image": "/static/img/use-cases/lebibi.png",
            "caption": "leBIBI uses RNAcentral as a reference data set for reconstructing the phylogeny of archaeal or bacterial sequences",
            "category": "reference-ncrna-set",
            "category_header": "Reference ncRNA set"
        },
        rainbowTroutPublication: {
            "title": "Genome-Wide Discovery of Long Non-Coding RNAs in Rainbow Trout.",
            "authors": ["Al-Tobasei R", "Paneru B", "Salem M"],
            "publication": "PLoS One. 2016 Feb 19;11(2):e0148940",
            "pubmed_id": 26895175,
            "doi": "10.1371/journal.pone.0148940",
            "pub_id": "",
            "image": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Lake_Washington_Ship_Canal_Fish_Ladder_pamphlet_-_male_freshwater_phase_Steelhead.jpg",
            "caption": "RNAcentral used as a reference data set to discover novel ncRNA in rainbow trout",
            "category": "reference-ncrna-set",
            "category_header": "Reference ncRNA set"
        },
        bovineLeukemiaPublication: {
            "title": "Characterization of novel Bovine Leukemia Virus (BLV) antisense transcripts by deep sequencing reveals constitutive expression in tumors and transcriptional interaction with viral microRNAs.",
            "authors": ["Durkin K", "Rosewick N", "Artesi M", "Hahaut V", "Griebel P", "Arsic N", "Burny A", "Georges M", "Van den Broeke A"],
            "publication": "Retrovirology. 2016 May 3;13(1):33",
            "pubmed_id": 27141823,
            "doi": "10.1186/s12977-016-0267-8",
            "pub_id": "",
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/8f/Fo%C3%BBboutaedje_fine_pea_ouy.JPG",
            "caption": "RNAcentral used as a reference data set to discover new ncRNA in Bovine Leukemia Virus",
            "category": "reference-ncrna-set",
            "category_header": "Reference ncRNA set"
        },
        goCurationPublication: {
            "title": "RNAcentral identifiers used to annotate human miRNAs with Gene Ontology terms",
            "authors": ["Huntley RP", "Sitnikov D", "Orlic-Milacic M", "Balakrishnan R", "D'Eustachio P", "Gillespie ME", "Howe D", "Kalea AZ", "Maegdefessel L", "Osumi-Sutherland D", "Petri V", "Smith JR", "Van Auken K", "Wood V", "Zampetaki A", "Mayr M", "Lovering RC"],
            "publication": "RNA. 2016 May;22(5):667-76",
            "pubmed_id": 26917558,
            "doi": "10.1261/rna.055301.115",
            "pub_id": "",
            "image": "/static/img/use-cases/go-curation.jpg", // "http://rnajournal.cshlp.org/content/22/5/667/F4.large.jpg",
            "caption": "RNAcentral identifiers used to annotate ncRNAs with Gene Ontology terms",
            "category": "literature-curation",
            "category_header": "Stable identifiers for ncRNAs"
        },
        yeastCurationPublication: {
            "title": "The yeast noncoding RNA interaction network.",
            "authors": ["Panni S", "Prakash A", "Bateman A", "Orchard S"],
            "publication": "RNA. 2017 Oct;23(10):1479-1492",
            "pubmed_id": 28701522,
            "doi": "10.1261/rna.060996.117",
            "pub_id": "",
            "image": "/static/img/use-cases/yeast-curation.gif", // "http://rnajournal.cshlp.org/content/23/10/1479/F2.small.gif",
            "caption": "RNAcentral identifiers used to annotate ncRNA interactions in yeast",
            "category": "literature-curation",
            "category_header": "Stable identifiers for ncRNAs"
        },
        secondaryStructurePredictionPublication: {
            "title": "Forna (force-directed RNA): Simple and effective online RNA secondary structure diagrams.",
            "authors": ["Kerpedjiev P", "Hammer S", "Hofacker IL"],
            "publication": "Bioinformatics. 2015 Oct 15;31(20):3377-9",
            "pubmed_id": 26099263,
            "doi": "10.1093/bioinformatics/btv372",
            "pub_id": "",
            "image": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4595900/bin/btv372f1p.jpg",
            "caption": "Source of sequences for secondary structure prediction",
            "category": "programmatic-information-retrieval",
            "category_header": "Programmatic information retrieval"
        },
        expandingHorizonsPublication: {
            "title": "Expanding the horizons of microRNA bioinformatics.",
            "authors": ["Huntley R", 'Kramarz B', 'Sawford T', 'Umrao Z', 'Kalea A', 'Acquaah V', 'Martin MJ', 'Mayr M', 'Lovering RC'],
            "publication": "RNA. 2018 Aug;24(8):1005-1017",
            "pubmed_id": 29871895,
            "doi": "10.1261/rna.065565.118",
            "pub_id": "",
            "image": "/static/img/use-cases/expanding-horizons.jpg", // "http://rnajournal.cshlp.org/content/24/8/1005/F2.large.jpg",
            "caption": "RNAcentral identifiers used to annotate ncRNAs with Gene Ontology terms",
            "category": "literature-curation",
            "category_header": "Stable identifiers for ncRNAs"
        },
        mg7MetagenomicPublication: {
            "title": "MG7: Configurable and scalable 16S metagenomics data analysis",
            "authors": ["Alexey Alekhin", 'Evdokim Kovach', 'Marina Manrique', 'Pablo Pareja-Tobes', 'Eduardo Pareja', 'Raquel Tobes', 'Eduardo Pareja-Tobes'],
            "publication": "bioRxiv 027714",
            "pubmed_id": "",
            "doi": "10.1101/027714",
            "pub_id": "",
            "image": "https://era7bioinformatics.com/en/download_area_image.cfm?id=464",
            "caption": "RNAcentral is used to build a reference database for metagenomics analysis using the MG7 pipeline",
            "category": "reference-ncrna-set",
            "category_header": "Reference ncRNA set"
        },
        anemoneMirnaPublication: {
            "title": "Evidence for miRNA-mediated modulation of the host transcriptome in cnidarian-dinoflagellate symbiosis.",
            "authors": ['Baumgarten S', 'Cziesielski MJ', 'Thomas L', 'Michell CT', 'Esherick LY', 'Pringle JR', 'Aranda M', 'Voolstra CR'],
            "publication": "Mol Ecol. 2018 Jan;27(2):403-418",
            "pubmed_id": 29218749,
            "doi": "10.1111/mec.14452",
            "pub_id": "",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/37/Aiptasia_2.jpg",
            "caption": "RNAcentral is used to identify ncRNAs in sea anemone Aiptasia",
            "category": "reference-ncrna-set",
            "category_header": "Reference ncRNA set"
        }
    }
};
useCasesService.$inject = [];

var useCasesController = function($scope, $location, $window, $rootScope, $http, routes, useCases) {
    $scope.routes = routes;  // expose routes in template for error message
    $scope.useCases = useCases;  // expose list of useCases to be reused here and in homepage
};

useCasesController.$inject = ['$scope', '$location', '$window', '$rootScope', '$http', 'routes', 'useCases'];


angular.module("useCases", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'rnaSequence'])
    .controller("useCasesController", useCasesController)
    .service("useCases", useCasesService);
