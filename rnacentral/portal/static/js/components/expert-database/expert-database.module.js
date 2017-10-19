var expertDatabaseController = function($scope, $location, $window, $rootScope) {
    $http
    $scope.expertDb =
};

expertDatabaseController.$inject = ['$scope', '$location', '$window', '$rootScope'];


angular.module("expertDatabase", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .controller("expertDatabaseController", expertDatabaseController);