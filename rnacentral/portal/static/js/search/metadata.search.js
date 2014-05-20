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
        hitCount: null,
        entries: [],
        facets: []
    }
    var show_results = false; // hide results section at first
    var search_in_progress = false;

    var search_config = {
        ebeye_base_url: 'http://ash-4.ebi.ac.uk:8080/ebisearch/ws/rest/rnacentral',
        rnacentral_base_url: get_base_url(),
        fields: ['description', 'active', 'length'],
        facetfields: ['expert_db', 'rna_type', 'TAXONOMY', 'active'], // will be displayed in this order
        facetcount: 30,
        page_size: 15,
        max_facet_count: 1000,
    };
    var page_size = search_config.page_size; // set to the default value

    var query_urls = {
        'ebeye_search': search_config.ebeye_base_url +
                        '?query={QUERY}' +
                        '&format=json' +
                        '&fields=' + search_config.fields.join() +
                        '&facetcount=' + search_config.facetcount +
                        '&facetfields=' + search_config.facetfields.join() +
                        '&size={SIZE}' +
                        '&start=0',
        'proxy': search_config.rnacentral_base_url +
                 '/api/internal/ebeye?url={EBEYE_URL}',
        'get_more_facet_values': search_config.ebeye_base_url +
                                 '?query={QUERY}' +
                                 '&format=json' +
                                 '&facetcount=' + search_config.max_facet_count +
                                 '&facetfields={FACET_ID}' +
                                 '&size=0', // retrieve just facets
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
        result.hitCount = data.hitCount;
        result.entries = data.entries;
        // sort facets the same way as in config
        result.facets = _.sortBy(data.facets, function(facet){
            return _.indexOf(search_config.facetfields, facet.id);
        });
    };

    /**
     * Format urls and execute remote request.
     */
    var execute_ebeye_search = function(url) {
        search_in_progress = true;
        $http({
            url: url,
            method: 'GET'
        }).success(function(data) {
            preprocess_results(data);
            search_in_progress = false;
        }).error(function(){
            search_in_progress = false;
        });
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
            result.hitCount = null;
        } else {
            // load_more_results search, use supplied new_page_size value
            page_size = new_page_size;
        }

        var ebeye_url = query_urls.ebeye_search.replace('{QUERY}', query).replace('{SIZE}', page_size);
        var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url));
        execute_ebeye_search(url);
    };

    /**
     * Increment `page_size` and retrieve all entries from the server.
     * The new entries will be added to the results list.
     */
    this.load_more_results = function() {
        page_size += search_config.page_size;
        query = $location.search().q;
        this.search(query, page_size);
    };

    this.load_more_facets = function(facet_id) {
        var query = $location.search().q;
        var ebeye_url = query_urls.get_more_facet_values.replace('{QUERY}', query).replace('{FACET_ID}', facet_id);
        var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url)) ;
        $http({
            url: url,
            method: 'GET'
        }).success(function(data) {
            // find where to insert new data
            var facet_num = _.indexOf(_.map(result.facets, function(facet){
                return facet['id'] === facet_id;
            }), true);
            result.facets[facet_num].facetValues = data.facets.facet.facetValues;
        });
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

    this.get_max_facet_count = function() {
        return search_config.max_facet_count;
    };

    this.get_search_in_progress = function() {
        return search_in_progress;
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
    $scope.max_facet_count = results.get_max_facet_count();
    $scope.search_in_progress = results.get_search_in_progress();

    /**
     * Refresh results data.
     */
    $scope.$watch(function () { return results.get_results(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result = newValue;
        }
    });

    /**
     * Monitor show_results changes.
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
     * Monitor search_in_progress changes.
     */
    $scope.$watch(function () { return results.get_search_in_progress(); }, function (newValue, oldValue) {
        if (newValue != oldValue) {
            $scope.search_in_progress = newValue;
        }
    });

    /**
     * Fired when "Load more" button is clicked.
     */
    $scope.load_more_results = function() {
        results.load_more_results();
    };

    $scope.load_more_facets = function(facet_id) {
        results.load_more_facets(facet_id);
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
        return Math.min($scope.page_size, $scope.result.hitCount);
    };

    /**
     * Show/hide search facets to save screen space.
     * Uses jQuery for simplicity.
     * Activated only on mobile devices.
     */
    $scope.toggle_facets = function() {
        var facets = $('.metasearch-facets');
        facets.toggleClass('hidden-xs', !facets.hasClass('hidden-xs'));
        $('#toggle-facets').text(function(i, text){
          return text === "Show facets" ? "Hide facets" : "Show facets";
        });
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
