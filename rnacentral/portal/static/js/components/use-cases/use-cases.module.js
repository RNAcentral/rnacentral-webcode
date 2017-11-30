var useCasesController = function($scope, $location, $window, $rootScope, $http, routes) {
    $scope.routes = routes;  // expose routes in template for error message


};

useCasesController.$inject = ['$scope', '$location', '$window', '$rootScope', '$http', 'routes'];


angular.module("useCases", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .controller("useCasesController", useCasesController);