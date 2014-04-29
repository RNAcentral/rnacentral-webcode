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

;var underscore = angular.module('underscore', []);
underscore.factory('_', function() {
    return window._;
});

var rnaMetasearch = angular.module('rnacentralApp', ['chieffancypants.loadingBar', 'underscore']);

rnaMetasearch.config(['$locationProvider', function($locationProvider) {
    $locationProvider.html5Mode(true);
}]);

/**
 * Service for passing data between controllers.
 */
rnaMetasearch.service('results', ['_', function(_) {
    var result;
    var show_results = false;

    /**
     * Process json files like this:
     * { "field" : [ {"id": "description", "values": {"value": "description_value"}} ] }
     * into key-value pairs like this:
     * {"description": "description_value"}
     */
    function flatten_entry_fields(ebeye_json) {
        var result = {
            'hits': ebeye_json.result.hitCount,
            'rnas': []
        }

        result.rnas = _.each(ebeye_json.result.entries.entry, function(entry){
            _.each(entry.fields.field, function(field){
                entry[field['@id']] = field.values.value;
            });
        });
        return result;
    };

    return {
        get_status: function() {
            return show_results;
        },
        set_status: function() {
            show_results = true;
        },
        store: function(data) {
            result = flatten_entry_fields(data);
            console.log(result);
        },
        get: function() {
            return result;
        }
    }
}]);

rnaMetasearch.controller('MainContent', ['$scope', '$anchorScroll', '$location', 'results', function($scope, $anchorScroll, $location, results) {

    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results= newValue;
           }
    });
}]);

rnaMetasearch.controller('ResultsListCtrl', ['$scope', 'results', function($scope, results) {

    $scope.result = results.get();
    $scope.show_results = results.get_status();

    $scope.$watch(function () { return results.get(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result= newValue;
           }
    });

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results= newValue;
           }
    });

}]);

rnaMetasearch.controller('QueryCtrl', ['$scope', '$http', '$location', 'results', function($scope, $http, $location, results) {

    $scope.query = {
        text: '',
        submitted: false
    };

    $scope.show_results = false;
    $scope.store_data = results.store;
    $scope.set_status = results.set_status;

    // watch url changes to perform a new search
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {

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


        var ebeye_url = 'http://ash-4.ebi.ac.uk:8080/ebisearch/ws/rest/rnacentral?query={QUERY}&fields=description,active,length,name&format=json';
        ebeye_url = ebeye_url.replace('{QUERY}', query);
        var url = 'http://localhost:8000/api/internal/ebeye?url=' + encodeURIComponent(ebeye_url);

        $http({
            url: url,
            method: 'GET'
            // params: {taxid: $scope.query.text}
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

    var check_if_search_url = function () {
       // check if there is query in url
        if ($location.url().indexOf("/search?q=") > -1) {
            // a search result page, launch a new search
            $scope.query.text = $location.search().q;
            $scope.search($location.search().q);
        }
    };

    // run once at initialisation
    check_if_search_url();
}]);
