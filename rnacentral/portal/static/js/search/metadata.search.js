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

;

/**
 * Make it possible to include underscore as a dependency.
 */
var underscore = angular.module('underscore', []);
underscore.factory('_', function() {
    return window._;
});

/**
 * Create RNAcentral app.
 */
var rnaMetasearch = angular.module('rnacentralApp', ['chieffancypants.loadingBar', 'underscore']);

/**
 * html5mode removes hashtags from urls.
 */
rnaMetasearch.config(['$locationProvider', function($locationProvider) {
    $locationProvider.html5Mode(true);
}]);

/**
 * Service for passing data between controllers.
 */
rnaMetasearch.service('results', ['_', '$http', function(_, $http) {
    var result = {
        hits: null,
        rnas: [],
        facets: []
    }
    var show_results = false;

    /**
     * Process deeply nested json objects like this:
     * { "field" : [ {"id": "description", "values": {"value": "description_value"}} ] }
     * into key-value pairs like this:
     * {"description": "description_value"}
     */
    var preprocess_results = function(data) {
        result.hits = data.result.hitCount;

        result.facets = _.each(data.result.facets.facet, function(facet){
            facet.facetValues.facetValue = wrap_in_array(facet.facetValues.facetValue);
            return facet;
        });

        data.result.entries.entry = wrap_in_array(data.result.entries.entry);
        result.rnas = _.each(data.result.entries.entry, function(entry){
            // flatten deeply nested arrays
            _.each(entry.fields.field, function(field){
                entry[field['@id']] = field.values.value;
            });
        });

        function wrap_in_array(data) {
            // wrap single entry in an array
            if ( !_.isArray(data) ) {
                return [data]
            } else {
                return data;
            }
        };
    };

    /**
     * Launch EBeye search
     */
    this.search = function(query) {
        // display results section
        show_results = true;

        var search_config = {
            ebeye_base_url: 'http://ash-4.ebi.ac.uk:8080',
            rnacentral_base_url: 'http://localhost:8000',
            fields: ['description', 'active', 'length', 'name'],
            facetfields: ['active', 'expert_db', 'rna_type', 'TAXONOMY'],
            facetcount: 10,
            page_size: 15 //$scope.query.size,
        };

        var query_urls = {
            'ebeye_search': search_config.ebeye_base_url +
                            '/ebisearch/ws/rest/rnacentral' +
                            '?query={QUERY}' +
                            '&format=json' +
                            '&fields=' + search_config.fields.join() +
                            '&facetcount=' + search_config.facetcount +
                            '&facetfields=' + search_config.facetfields.join() +
                            '&size=15' +
                            '&start=0',
            'proxy': search_config.rnacentral_base_url +
                     '/api/internal/ebeye?url={EBEYE_URL}'
        };

        var ebeye_url = query_urls.ebeye_search.replace('{QUERY}', query); //.replace('{SIZE}', $scope.query.size);
        var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url));
        $http({
            url: url,
            method: 'GET'
        }).success(function(data) {
            preprocess_results(data);
        });
    };


    this.get_status = function() {
        return show_results;
    };

    this.set_status = function() {
        show_results = true;
    };

    this.get_results = function() {
        return result;
    };

}]);

rnaMetasearch.controller('MainContent', ['$scope', '$anchorScroll', '$location', 'results', function($scope, $anchorScroll, $location, results) {
    /**
     * Enables scrolling to anchor tags.
     * <a ng-click="scrollTo('anchor')">Title</a>
     */
    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    /**
     * Watch show_results in order to hide non-search-related content
     * when a search is initiated.
     */
    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results = newValue;
        }
    });

}]);

rnaMetasearch.controller('ResultsListCtrl', ['$scope', 'results', function($scope, results) {
    $scope.$watch(function () { return results.get_results(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result = newValue;
        }
    });

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results = newValue;
        }
    });

}]);

rnaMetasearch.controller('QueryCtrl', ['$scope', '$location', 'results', function($scope, $location, results) {

    $scope.query = {
        text: '',
        submitted: false
    };

    // watch url changes to perform a new search
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {

         // a regular non-search url, potentially unchanged
        if (newUrl !== oldUrl) {
            if (newUrl.indexOf('/search') == -1) {
                // not a search page, redirect
                window.location.href = newUrl;
            } else {
                // a search result page, launch a new search
                $scope.query.text = $location.search().q;
                results.search($location.search().q);
                $scope.query.submitted = false;
            }
        }
    });

    $scope.search = function(query) {
        $location.url('/search' + '?q=' + query);
    }

    $scope.submit_query = function() {
        $scope.query.submitted = true;
        if ($scope.queryForm.text.$invalid) {
            return;
        }
        $scope.search($scope.query.text);
    };

    /**
     * Check if the url contains a query when the controller is first created
     * and initiate a search if necessary.
     */
    (function () {
        if ($location.url().indexOf("/search?q=") > -1) {
            // a search result page, launch a new search
            $scope.query.text = $location.search().q;
            results.search($location.search().q);
        }
    })();

}]);
