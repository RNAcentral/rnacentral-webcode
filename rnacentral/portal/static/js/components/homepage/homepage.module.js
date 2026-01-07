var HomepageController = function($scope) {
    $scope.RNAcentralPublication = {
        "title": "RNAcentral in 2026: genes and literature integration",
        "authors": ["The RNAcentral Consortium"],
        "publication": "Nucleic Acids Res. 2025",
        "pubmed_id": 41404707,
        "doi": "10.1093/nar/gkaf1329",
        "pub_id": ""
    }
};
HomepageController.$inject = ['$scope'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
