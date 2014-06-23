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
var rnaMetasearch = angular.module('rnacentralApp', ['chieffancypants.loadingBar', 'underscore', 'ngAnimate']);

// hide spinning wheel
rnaMetasearch.config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeSpinner = false;
}]);

/**
 * html5mode removes hashtags from urls.
 */
rnaMetasearch.config(['$locationProvider', function($locationProvider) {
    $locationProvider.html5Mode(true);
}]);


/**
 * Service for launching a metadata search.
 */
rnaMetasearch.service('search', ['$location', function($location) {

    /**
     * To launch a new search, change browser url,
     * which will automatically trigger a new search
     * since the url changes are watched in the query controller.
     */
    this.meta_search = function(query) {
        $location.url('/search' + '?q=' + query);
    };

}]);

/**
 * Service for passing data between controllers.
 */
rnaMetasearch.service('results', ['_', '$http', '$location', '$window', function(_, $http, $location, $window) {

    /**
     * Service initialization.
     */
    var result = {
        hitCount: null,
        entries: [],
        facets: [],
    };

    var status = {
        display_search_interface: false, // hide results section at first
        search_in_progress: false, // display spinning wheel while searching
        show_error: false, // display error message
    };

    var search_config = {
        ebeye_base_url: 'http://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral',
        rnacentral_base_url: get_base_url(),
        fields: ['description', 'active', 'length'],
        facetfields: ['expert_db', 'rna_type', 'TAXONOMY'], // will be displayed in this order
        facetcount: 30,
        pagesize: 15,
    };

    var query_urls = {
        'ebeye_search': search_config.ebeye_base_url +
                        '?query={QUERY}' +
                        '&format=json' +
                        '&fields=' + search_config.fields.join() +
                        '&facetcount=' + search_config.facetcount +
                        '&facetfields=' + search_config.facetfields.join() +
                        '&size=' + search_config.pagesize +
                        '&start={START}',
        'proxy': search_config.rnacentral_base_url +
                 '/api/internal/ebeye?url={EBEYE_URL}',
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
    }

    /**
     * Launch EBeye search.
     * `start` determines the range of the results to be returned.
     */
    this.search = function(query, start) {
        start = start || 0;

        display_search_interface();
        display_spinner();
        update_page_title();

        query = preprocess_query(query);
        query_url = get_query_url(query, start);
        execute_ebeye_search(query_url, start === 0);

        /**
         * Display search spinner if not a "load more" request.
         */
        function display_spinner() {
            if (start === 0) {
                result.hitCount = null; // display spinner
            }
        }

        /**
         * Change page title, which is also used in browser tabs.
         */
        function update_page_title() {
            $window.document.title = 'Search: ' + query;
        }

        /**
         * Setting `display_search_interface` value to true hides all non-search page content
         * and begins displaying search results interface.
         */
        function display_search_interface() {
            status.display_search_interface = true;
        }

        /**
         * Create an RNAcentral proxy query url which includes EBeye query url.
         */
        function get_query_url() {
            var ebeye_url = query_urls.ebeye_search.replace('{QUERY}', query).replace('{START}', start);
            var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url));
            return url;
        }

        /**
         * Split query into words and then:
         *  - append wildcards to all terms without double quotes and not ending with wildcards
         *  - escape special symbols
         *  - capitalize logical operators
         *
         *  Splitting into words is based on this SO question:
         *  http://stackoverflow.com/questions/366202/regex-for-splitting-a-string-using-space-when-not-surrounded-by-single-or-double
         * Each "word" is a sequence of characters that aren't spaces or quotes,
         * or a sequence of characters that begin and end with a quote, with no quotes in between.
         */
        function preprocess_query(query) {
            var words = query.match(/[^\s"]+|"[^"]*"/g);
            var array_length = words.length;
            for (var i = 0; i < array_length; i++) {
                if ( words[i].match(/and|or|not/gi) ) {
                    // capitalize logical operators
                    words[i] = words[i].toUpperCase();
                } else if ( words[i].match(/\:$/gi) ) {
                    // faceted search term, do nothing
                } else if ( words[i].match(/^".+?"$/) ) {
                    // double quotes, do nothing
                } else if ( words[i].match(/\*$/) ) {
                    // wildcard, escape term
                    words[i] = escape_search_term(words[i]);
                } else if ( words[i].match(/\)$/) ) {
                    // right closing grouping parenthesis, don't add a wildcard
                } else {
                    // all other words
                    // escape term, add wildcard
                    words[i] = escape_search_term(words[i]) + '*';
                };
            }
            query = words.join(' ');
            return query;

            /**
             * Escape special symbols used by Lucene
             * Escaped: + - && || ! { } [ ] ^ ~ ? : \
             * Not escaped: * " ( ) because they may be used deliberately by the user
             */
            function escape_search_term(search_term) {
                return search_term.replace(/[\+\-&|!\{\}\[\]\^~\?\:\\]/g, "\\$&");
            }
        }

        /**
         * Execute remote request.
         */
        function execute_ebeye_search(url, overwrite_results) {
            status.search_in_progress = true;
            status.show_error = false;
            $http({
                url: url,
                method: 'GET'
            }).success(function(data) {
                data = preprocess_results(data);
                overwrite_results = overwrite_results || false;
                if (overwrite_results) {
                    result = data; // replace
                } else {
                    // append only entries
                    result.entries = result.entries.concat(data.entries);
                }
                status.search_in_progress = false;
            }).error(function(){
                status.search_in_progress = false;
                status.show_error = true;
            });

            /**
             * Preprocess data received from the server.
             */
            function preprocess_results(data) {
                // sort facets the same way as in config
                _.sortBy(data.facets, function(facet){
                    return _.indexOf(search_config.facetfields, facet.id);
                });
                return data;
            }
        }

    }

    /**
     * Load more results starting from the last loaded index.
     */
    this.load_more_results = function() {
        query = $location.search().q;
        this.search(query, result.entries.length);
    };

    /**
     * Broadcast whether search interface should be displayed.
     */
    this.get_status = function() {
        return status.display_search_interface;
    };

    /**
     * Broadcast search results changes.
     */
    this.get_result = function() {
        return result;
    };

    /**
     * Broadcast whether search is in progress.
     */
    this.get_search_in_progress = function() {
        return status.search_in_progress;
    };

    /**
     * Broadcast whether an error has occurred.
     */
    this.get_show_error = function() {
        return status.show_error;
    };

}]);

rnaMetasearch.controller('MainContent', ['$scope', '$anchorScroll', '$location', 'results', 'search', function($scope, $anchorScroll, $location, results, search) {
    /**
     * Enables scrolling to anchor tags.
     * <a ng-click="scrollTo('anchor')">Title</a>
     */
    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    /**
     * Watch `display_search_interface` in order to hide non-search-related content
     * when a search is initiated.
     */
    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.display_search_interface = newValue;
        }
    });

    /**
     * Launch a metadata search from a web page.
     */
    $scope.meta_search = function(query) {
        search.meta_search(query);
    };

}]);

/**
 * Results display controller
 * Responsible for visualising search results.
 */
rnaMetasearch.controller('ResultsListCtrl', ['$scope', '$location', 'results', function($scope, $location, results) {

    $scope.result = {
        entries: [],
    };

    $scope.search_in_progress = results.get_search_in_progress();
    $scope.show_error = results.get_show_error();

    /**
     * Watch `result` changes.
     */
    $scope.$watch(function () { return results.get_result(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result = newValue;
        }
    });

    /**
     * Watch `display_search_interface` changes.
     */
    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.display_search_interface = newValue;
        }
    });

    /**
     * Watch `search_in_progress` changes.
     */
    $scope.$watch(function () { return results.get_search_in_progress(); }, function (newValue, oldValue) {
        if (newValue != oldValue) {
            $scope.search_in_progress = newValue;
        }
    });

    /**
     * Watch `show_error` changes.
     */
    $scope.$watch(function () { return results.get_show_error(); }, function (newValue, oldValue) {
        if (newValue != oldValue) {
            $scope.show_error = newValue;
        }
    });

    /**
     * Fired when "Load more" button is clicked.
     */
    $scope.load_more_results = function() {
        results.load_more_results();
    };

    /**
     * Determine if the facet has already been applied.
     */
    $scope.is_facet_applied = function(facet_id, facet_value) {
        var query = $location.search().q || '';
        var facet_query = facet_id + ':"' + facet_value + '"';
        if (query.indexOf(facet_query) == -1) {
            return false;
        } else {
            return true;
        }
    };

    /**
     * Run a search with a facet enabled.
     * The facet will be toggled on and off in the repeated calls with the same
     * parameters.
     */
    $scope.facet_search = function(facet_id, facet_value) {
        var query = $location.search().q || '';
        var facet_query = ' AND ' + facet_id + ':"' + facet_value + '"';
        if ($scope.is_facet_applied(facet_id, facet_value)) {
            new_query = query.replace(facet_query, ''); // remove facet
        } else {
            new_query = query + facet_query; // add new facet
        }
        $location.search('q', new_query);
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
rnaMetasearch.controller('QueryCtrl', ['$scope', '$location', '$window', '$timeout', 'results', 'search', function($scope, $location, $window, $timeout, results, search) {

    $scope.query = {
        text: '',
        submitted: false
    };

    /**
     * Launch a metadata search using the service.
     */
    $scope.meta_search = function(query) {
        search.meta_search(query);
    };

    /**
     * Control browser navigation buttons.
     */
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {
        // ignore url hash
        newUrl = newUrl.replace(/#.+$/, '');
        oldUrl = oldUrl.replace(/#.+$/, '');
        // url has changed
        if (newUrl !== oldUrl) {
            if (newUrl.indexOf('/search') == -1) {
                // a non-search url, load that page
                $timeout(function() {
                    // wrapping in $timeout to avoid "digest in progress" errors
                    $window.location = newUrl;
                });
            } else {
                // the new url is a search result page, launch that search
                $scope.query.text = $location.search().q;
                results.search($location.search().q);
                $scope.query.submitted = false;
            }
        }
    });

    /**
     * Called when the form is submitted.
     */
    $scope.submit_query = function() {
        $scope.query.submitted = true;
        if ($scope.queryForm.text.$invalid) {
            return;
        }
        $scope.meta_search($scope.query.text);
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
