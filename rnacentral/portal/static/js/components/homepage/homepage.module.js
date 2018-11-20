var HomepageController = function($scope, useCases) {
    $scope.useCases = useCases;  // expose useCases to the templates

    /**
     * Generate one example per useCases category
     * @param {Object} useCases
     * @returns {Object} - an object: { <categoryName>: <useCase> }, e.g.:
     *   {
     *     "reference-ncrna-set": [Object object],
     *     "literature-curation": [Object object],
     *     "programmatic-information-retrieval": [Object object]
     *   }
     */
    function generateRandomExamples(useCases) {
        // generate a non-redundant list of categories
        var categories = Array.from(new Set(Object.values(useCases).map(function(value) { return value.category })));

        var output = [];
        categories.forEach(function(category) {
            var categoryMembers = Object.values(useCases).filter(function(useCase) { return useCase.category === category });
            var randomIndex = Math.floor(Math.random() * categoryMembers.length);
            output.push(categoryMembers[randomIndex]);
        });

        return output;
    }

    $scope.randomExamples = generateRandomExamples(useCases);

    $scope.RNAcentralPublication = {
        "title": "RNAcentral: a hub of information for non-coding RNA sequences",
        "authors": ["The RNAcentral Consortium"],
        "publication": "Nucleic Acids Res. 2019",
        "pubmed_id": 30395267,
        "doi": "10.1093/nar/gky1034",
        "pub_id": ""
    }
};
HomepageController.$inject = ['$scope', 'useCases'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'useCases', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
