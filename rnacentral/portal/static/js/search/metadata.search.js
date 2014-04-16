/*
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// RNAcentral metasearch app.

;var rnaMetasearch = angular.module('rnacentralApp', ['chieffancypants.loadingBar']);

rnaMetasearch.config(['$locationProvider', function($locationProvider) {
    $locationProvider.html5Mode(true);
}]);

rnaMetasearch.service('results', function() {
    var rnas = [];
    var show_results = false;

    return {
        get_status: function() {
            return show_results;
        },
        set_status: function() {
            show_results = true;
        },
        store: function(data) {
            rnas = data;
        },
        get: function() {
            return rnas;
        }
    }
});

rnaMetasearch.controller('MainContent', function($scope, $anchorScroll, $location, results) {

    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results= newValue;
           }
    });
});

// minification-safe method
// phonecatApp.controller('PhoneListCtrl', ['$scope', '$http', function($scope, $http) {...}]);

rnaMetasearch.controller('ResultsListCtrl', function($scope, results) {

    $scope.rnas = results.get();
    $scope.show_results = results.get_status();

    $scope.$watch(function () { return results.get(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.rnas= newValue;
           }
    });

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results= newValue;
           }
    });

});

rnaMetasearch.controller('QueryCtrl', function($scope, $http, $location, results) {

    $scope.query = {
        text: '',
        submitted: false
    };

    $scope.show_results = false;
    $scope.store_data = results.store;
    $scope.set_status = results.set_status;

    // watch url changes to perform a new search
    // TODO resolve conflict with anchor tag navigation and bootstrap tabs
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {

    	// TODO: initialize the search when going to a search url
    	// this function only executes on url update

         // a regular non-search url, potentially unchanged
        if (newUrl !== oldUrl) {
            if (newUrl.indexOf('/search') == -1) {
                // not a search page, redirect
                console.log('About to redirect ' + window.location.pathname);
                window.location.href = newUrl;
            } else {
                // a search result page, launch a new search
                $scope.query.text = $location.search().q;
                $scope.search($location.search().q);
            }
        }
    });

    $scope.search = function(query) {
        $scope.query.text = query;
        $scope.show_results = true;
        $scope.set_status();
        $location.url('/search' + '?q=' + query);
        $http({
            url: '/api/v1/search',
            method: 'GET',
            params: {taxid: $scope.query.text}
        }).success(function(data) {
            $scope.store_data(data);
            $scope.query.submitted = false;
        });
    }

    $scope.submit_query = function() {
        $scope.query.submitted = true;
        if ($scope.queryForm.text.$invalid) {
            return;
        }

        $scope.search($scope.query.text);
    };

});
