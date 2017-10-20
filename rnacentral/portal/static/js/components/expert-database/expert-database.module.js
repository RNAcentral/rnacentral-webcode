var expertDatabaseController = function($scope, $location, $window, $rootScope, routes) {
    $http.get(routes.expertDbsApi).then(
        function(response) {
            $scope.expertDb = reponse.data;
        },
        function(response) {}
    )
};

expertDatabaseController.$inject = ['$scope', '$location', '$window', '$rootScope', 'routes'];


angular.module("expertDatabase", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .controller("expertDatabaseController", expertDatabaseController);