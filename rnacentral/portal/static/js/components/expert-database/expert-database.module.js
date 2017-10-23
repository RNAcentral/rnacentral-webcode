var expertDatabaseController = function($scope, $location, $window, $rootScope, $http, routes) {
    // initialize $scope variables
    $scope.dbName = $location.path().split('/')[2];
    $scope.expertDb = null;
    $scope.error = false;  // if this flag is true, request to server failed - show error message template
    $scope.routes = routes;  // expose routes in template for error message

    // pass this down to components to receive errors from them
    $scope.onError = function() {
        $scope.error = true;
    };

    // download expertDbs json from server, pick appropriate database from it
    $http.get(routes.expertDbsApi()).then(
        function(response) {
            // find this particular database in array, returned from server
            for (var i = 0; i < response.data.length; i++) {
                if (response.data[i].label === $scope.dbName) {
                    $scope.expertDb = response.data[i];
                    break;
                }
                if (i === response.data.length - 1) {
                    console.log("Something's wrong, I can't find database '" + $scope.dbName + "' in our databases list");
                }
            }
        },
        function(response) {
            $scope.error = true;
        }
    )
};

expertDatabaseController.$inject = ['$scope', '$location', '$window', '$rootScope', '$http', 'routes'];


angular.module("expertDatabase", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .controller("expertDatabaseController", expertDatabaseController);