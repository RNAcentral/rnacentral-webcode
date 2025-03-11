var HomepageController = function($scope) {
    $scope.RNAcentralPublication = {
        "title": "RNAcentral 2021: secondary structure integration, improved sequence search and new member databases",
        "authors": ["The RNAcentral Consortium"],
        "publication": "Nucleic Acids Res. 2020",
        "pubmed_id": 33106848,
        "doi": "10.1093/nar/gkaa921",
        "pub_id": ""
    }
};
HomepageController.$inject = ['$scope'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
