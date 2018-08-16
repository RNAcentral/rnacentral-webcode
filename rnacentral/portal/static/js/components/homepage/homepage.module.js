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
        var categories = [...new Set(Object.values(useCases).map(value => value.category))];

        var output = []
        categories.forEach(function(category) {
            var categoryMembers = Object.values(useCases).filter(useCase => useCase.category === category);
            var randomIndex = Math.floor(Math.random() * categoryMembers.length);
            output.push(categoryMembers[randomIndex]);
        });

        return output
    };

    $scope.randomExamples = generateRandomExamples(useCases);
};
HomepageController.$inject = ['$scope', 'useCases'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'useCases', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
