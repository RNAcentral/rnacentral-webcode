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

/**
 * RNAcentral metadata search Angular.js app.
 */

; // concatenation safeguard

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
rnaMetasearch.service('results', ['_', '$http', '$location', '$window', function(_, $http, $location, $window) {
    var result = {
        hits: null,
        rnas: [],
        facets: []
    }
    var show_results = false; // hide results section at first

    var search_config = {
        ebeye_base_url: 'http://ash-4.ebi.ac.uk:8080',
        rnacentral_base_url: get_base_url(),
        fields: ['description', 'active', 'length', 'name'],
        facetfields: ['active', 'expert_db', 'rna_type', 'TAXONOMY'],
        facetcount: 10,
        page_size: 15
    };
    var page_size = search_config.page_size; // set to the default value

    var query_urls = {
        'ebeye_search': search_config.ebeye_base_url +
                        '/ebisearch/ws/rest/rnacentral' +
                        '?query={QUERY}' +
                        '&format=json' +
                        '&fields=' + search_config.fields.join() +
                        '&facetcount=' + search_config.facetcount +
                        '&facetfields=' + search_config.facetfields.join() +
                        '&size={SIZE}' +
                        '&start=0',
        'proxy': search_config.rnacentral_base_url +
                 '/api/internal/ebeye?url={EBEYE_URL}'
    };

    /**
     * Calculate base url for production and development environments.
     */
    function get_base_url() {
        var base_url = $location.protocol() + '://' + $location.host();
        var port = $location.port();
        if (port !== '') {
            base_url += ':' + port
        }
        return base_url;
    };

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
    this.search = function(query, new_page_size) {
        // display results section
        show_results = true;
        // update page title
        $window.document.title = 'Search: ' + query;

        if (typeof(new_page_size) == "undefined") {
            // if unspecified, use default
            page_size = search_config.page_size;
            // initial search, display spinner
            result.hits = null;
        } else {
            // load_more search, use supplied new_page_size value
            page_size = new_page_size;
        }

        var ebeye_url = query_urls.ebeye_search.replace('{QUERY}', query).replace('{SIZE}', page_size);
        var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url));
        $http({
            url: url,
            method: 'GET'
        }).success(function(data) {
            preprocess_results(data);
        });
    };

    /**
     * Increment `page_size` and retrieve all entries from the server.
     * The new entries will be added to the results list.
     */
    this.load_more = function() {
        page_size += search_config.page_size;
        query = $location.search().q;
        this.search(query, page_size);
    };

    this.get_page_size = function() {
        return page_size;
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

/**
 * Results display controller
 * Responsible for visualising search results.
 */
rnaMetasearch.controller('ResultsListCtrl', ['$scope', '$location', 'results', function($scope, $location, results) {

    $scope.page_size = results.get_page_size(); // know when to show Load more button

    /**
     * Refresh results data.
     */
    $scope.$watch(function () { return results.get_results(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result = newValue;
        }
    });

    /**
     * Get notified when show_results changes.
     */
    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results = newValue;
        }
    });

    /**
     * Monitor page_size changes.
     */
    $scope.$watch(function () { return results.get_page_size(); }, function (newValue, oldValue) {
        if (newValue != oldValue) {
            $scope.page_size = newValue;
        }
    });

    /**
     * Fired when "Load more" button is clicked.
     */
    $scope.load_more = function() {
        results.load_more();
    };

    /**
     * Repeat a search with a facet enabled.
     */
    $scope.facet_search = function(facet_id, facet_value) {
        var query = $location.search().q;
        var new_query = query + ' AND ' + facet_id + ':"' + facet_value + '"';
        $location.search('q', new_query);
    };

    /**
     * Calculate the number of currently displayed items.
     */
    $scope.displayed_items = function() {
        return Math.min($scope.page_size, $scope.result.hits);
    };

}]);

/**
 * Query controller
 * Responsible for the search box in the header.
 */
rnaMetasearch.controller('QueryCtrl', ['$scope', '$location', 'results', function($scope, $location, results) {

    $scope.query = {
        text: '',
        submitted: false
    };

    /**
     * Control browser navigation buttons.
     */
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {
        // url has changed
        if (newUrl !== oldUrl) {
            if (newUrl.indexOf('/search') == -1) {
                // a non-search url, load that page
                window.location.href = newUrl;
            } else {
                // the new url is a search result page, launch that search
                $scope.query.text = $location.search().q;
                results.search($location.search().q);
                $scope.query.submitted = false;
            }
        }
    });

    /**
     * To launch a new search, change browser url,
     * which will automatically trigger a new search because the url changes
     * are watched.
     */
    $scope.search = function(query) {
        $location.url('/search' + '?q=' + query);
    }

    /**
     * Called when the form is submitted.
     */
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
