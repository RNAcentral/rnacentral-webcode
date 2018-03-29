var expertDatabaseController = function($scope, $location, $window, $rootScope, $http, routes) {
    // initialize $scope variables
    $scope.dbName = $location.path().split('/')[2].toLowerCase();
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
                    $scope.error = true;
                }
            }

            // convert $scope.expertDb.references.authors into Array
            for (i = 0; i < $scope.expertDb.references.length; i++) {
                var reference = $scope.expertDb.references[i];
                var authors = reference.authors.split(',');

                // strip 'et al.' from last element, if present
                var last = authors[authors.length - 1];
                if (last && last.indexOf('et al.') !== -1) last = last.slice(0, last.indexOf('et al.'));
                authors[authors.length - 1] = last;

                // replace string authors with array
                reference.authors = authors;
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