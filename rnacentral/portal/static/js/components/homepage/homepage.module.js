var HomepageController = function($scope, useCases) {
    $scope.useCases = useCases;  // expose useCases to the templates
};
HomepageController.$inject = ['$scope', 'useCases'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes', 'useCases', 'rnaSequence'])
    .controller("HomepageController", HomepageController);
