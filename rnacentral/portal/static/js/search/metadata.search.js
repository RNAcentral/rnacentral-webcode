/*
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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
 * Service for launching a metadata search.
 */

var search = function(_, $http, $interpolate, $location, $window) {
    var self = this; // in case some event handler or constructor overrides "this"

    /**
     * Service initialization.
     */
    this.result = {
        hitCount: null,
        entries: [],
        facets: [],
        _query: null, // query after preprocessing
    };

    this.status = 'off'; // possible values: 'off', 'initiating', 'in progress', 'success', 'error'

    this.config = {
        ebeyeBaseUrl: global_settings.EBI_SEARCH_ENDPOINT,
        rnacentralBaseUrl: window.location.origin, // e.g. http://localhost:8000 or http://rnacentral.org
        fields: ['description', 'active', 'length', 'pub_title', 'has_genomic_coordinates'],
        facetfields: ['rna_type', 'TAXONOMY', 'expert_db', 'has_genomic_coordinates', 'popular_species'], // will be displayed in this order
        facetcount: 30,
        pagesize: 15,
    };

    this.queryUrls = {
        'ebeyeSearch': self.config.ebeyeBaseUrl +
                        '?query={{ query }}' +
                        '&format=json' +
                        '&hlfields=' + self.config.fields.join() +
                        '&facetcount=' + self.config.facetcount +
                        '&facetfields=' + self.config.facetfields.join() +
                        '&size=' + self.config.pagesize +
                        '&start={{ start }}' +
                        '&sort=boost:descending,length:descending' +
                        '&hlpretag=<span class=metasearch-highlights>&hlposttag=</span>',
        'ebeyeAutocomplete': 'http://www.ebi.ac.uk/ebisearch/ws/rest/RNAcentral/autocomplete' +
                              '?term={{ query }}' +
                              '&format=json',
        'proxy': self.config.rnacentralBaseUrl +
                 '/api/internal/ebeye?url={{ ebeyeUrl }}',
    };

    this.autocomplete = function(query) {
        // get queryUrl ready
        var ebeyeUrl = $interpolate(self.queryUrls.ebeyeAutocomplete)({query: query});
        var queryUrl = $interpolate(self.queryUrls.proxy)({ebeyeUrl: encodeURIComponent(ebeyeUrl)});

        return $http.get(queryUrl);
    };

    /**
     * Launch EBeye search.
     * `start` determines the range of the results to be returned.
     */
    this.search = function(query, start) {
        start = start || 0;

        hopscotch.endTour(); // end guided tour when a search is launched

        self.status = 'initiating';

        // display search spinner if not a "load more" request
        if (start === 0) self.result.hitCount = null;

        // change page title, which is also used in browser tabs
        $window.document.title = 'Search: ' + query;

        query = self.preprocessQuery(query);

        // get queryUrl ready
        var ebeyeUrl = $interpolate(self.queryUrls.ebeyeSearch)({query: query, start: start});
        var queryUrl = $interpolate(self.queryUrls.proxy)({ebeyeUrl: encodeURIComponent(ebeyeUrl)});

        // perform search
        var overwriteResults = (start === 0);

        self.promise = $http.get(queryUrl).then(
            function(response) {
                var data = self.preprocessResults(response.data);

                overwriteResults = overwriteResults || false;
                if (overwriteResults) {
                    data._query = self.result._query;
                    self.result = data; // replace
                } else {
                    self.result.entries = self.result.entries.concat(data.entries); // append new entries
                }

                self.status = 'success';
            },
            function(response) {
                self.status = 'error';
            }
        );
    };

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
    this.preprocessQuery = function(query) {

        // replace URS/taxid with URS_taxid - replace slashes with underscore
        query = query.replace(/(URS[0-9A-F]{10})\/(\d+)/ig, '$1_$2');

        // replace length query with a placeholder, example: length:[100 TO 200]
        var lengthClause = query.match(/length\:\[\d+\s+to\s+\d+\]/i);
        var placeholder = 'length_clause';
        if (lengthClause) {
          query = query.replace(lengthClause[0], placeholder);
          lengthClause[0] = lengthClause[0].replace(/to/i, 'TO');
        }

        var words = query.match(/[^\s"]+|"[^"]*"/g);
        var arrayLength = words.length;
        for (var i = 0; i < arrayLength; i++) {
            if ( words[i].match(/^(and|or|not)$/gi) ) {
                // capitalize logical operators
                words[i] = words[i].toUpperCase();
            } else if ( words[i].match(/\:$/gi) ) {
                // faceted search term + a colon, e.g. expert_db:
                var term = words[i].replace(':','');
                var xrefs = ['pubmed', 'doi', 'taxonomy'];
                if ( term.match(new RegExp('^(' + xrefs.join('|') + ')$', 'i') ) ) {
                    // xref fields must be capitalized
                    term = term.toUpperCase();
                }
                words[i] = term + ':';
            } else if ( words[i].match(/\//)) {
                // do not add wildcards to DOIs
                words[i] = escapeSearchTerm(words[i]);
            } else if ( words[i].match(/^".+?"$/) ) {
                // double quotes, do nothing
            } else if ( words[i].match(/\*$/) ) {
                // wildcard, escape term
                words[i] = escapeSearchTerm(words[i]);
            } else if ( words[i].match(/\)$/) ) {
                // right closing grouping parenthesis, don't add a wildcard
            } else if ( words[i].length < 3 ) {
                // the word is too short for wildcards, do nothing
            } else {
                // all other words
                // escape term, add wildcard
                words[i] = escapeSearchTerm(words[i]) + '*';
            }
        }
        query = words.join(' ');
        query = query.replace(/\: /g, ':'); // to avoid spaces after faceted search terms
        // replace placeholder with the original search term
        if (lengthClause) {
          query = query.replace(placeholder + '*', lengthClause[0]);
        }
        self.result._query = query;
        return query;

        /**
         * Escape special symbols used by Lucene
         * Escaped: + - && || ! { } [ ] ^ ~ ? : \ /
         * Not escaped: * " ( ) because they may be used deliberately by the user
         */
        function escapeSearchTerm(searchTerm) {
            return searchTerm.replace(/[\+\-&|!\{\}\[\]\^~\?\:\\\/]/g, "\\$&");
        }
    };

    /**
     * Preprocess data received from the server.
     */
    this.preprocessResults = function(data) {

        _mergeSpeciesFacets(data);

        // order facets the same way as in the config
        data.facets = _.sortBy(data.facets, function(facet){
            return _.indexOf(self.config.facetfields, facet.id);
        });

         // Use `hlfields` with highlighted matches instead of `fields`.
        for (var i=0; i < data.entries.length; i++) {
            data.entries[i].fields = data.entries[i].highlights;
            data.entries[i].fields.length[0] = data.entries[i].fields.length[0].replace(/<[^>]+>/gm, '');
            data.entries[i].id_with_slash = data.entries[i].id.replace('_', '/');
        }

        return data;

        /**
         * Merge the two species facets putting popularSpecies
         * at the top of the list.
         * Species facets:
         * - TAXONOMY (all species)
         * - popularSpecies (manually curated set of top organisms).
         */
        function _mergeSpeciesFacets(data) {

            // find the popular species facet
            var topSpeciesFacetId = _findFacetId('popular_species', data);

            if (topSpeciesFacetId) {
                // get top species names
                var popularSpecies = _.pluck(data.facets[topSpeciesFacetId].facetValues, 'label');

                // find the taxonomy facet
                var taxonomyFacetId = _findFacetId('TAXONOMY', data);

                // extract other species from the taxonomy facet
                var otherSpecies = _getOtherSpecies(data);

                // merge popularSpecies with otherSpecies
                data.facets[taxonomyFacetId].facetValues = data.facets[topSpeciesFacetId].facetValues.concat(otherSpecies);

                // remove the Popular species facet
                delete data.facets[topSpeciesFacetId];
                data.facets = _.compact(data.facets);
            }

            /**
             * Find objects in array by attribute value.
             * Given an array like:
             * [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
             * findFacetId('b') -> 1
             */
            function _findFacetId(facetLabel, data) {
                var index;
                _.find(data.facets, function(facet, i) {
                    if (facet.id === facetLabel) {
                        index = i;
                        return true;
                    }
                });
                return index;
            }

            /**
             * Get Taxonomy facet values that are not also in popularSpecies.
             */
            function _getOtherSpecies(data) {
                var taxonomyFacet = data.facets[taxonomyFacetId].facetValues;
                var otherSpecies = [];
                for (var i=0; i<taxonomyFacet.length; i++) {
                    if (_.indexOf(popularSpecies, taxonomyFacet[i].label) === -1) {
                        otherSpecies.push(taxonomyFacet[i]);
                    }
                }
                return otherSpecies;
            }
        }
    };

    /**
     * Load more results starting from the last loaded index.
     */
    this.loadMoreResults = function() {
        query = $location.search().q;
        this.search(query, self.result.entries.length);
    };
};

var MainContent = function($scope, $anchorScroll, $location, search) {
    $scope.displaySearchInterface = false;

    /**
     * Enables scrolling to anchor tags.
     * <a ng-click="scrollTo('anchor')">Title</a>
     */
    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    /**
     * Watch `displaySearchInterface` in order to hide non-search-related content
     * when a search is initiated.
     */
    $scope.$watch(function() { return search.status; }, function (newValue, oldValue) {
        if (newValue !== null) {
            $scope.displaySearchInterface = !(newValue === 'off');
        }
    });
};


var metadataSearchResults = {
    bindings: {},
    templateUrl: '/static/js/search/metadata-search-results.html',
    controller: ['$location', '$http', 'search', function($location, $http, search) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // variables that control UI state
            ctrl.result = { entries: [] };
            ctrl.showExportError = false;
            ctrl.status = search.status;

            // urls used in template (hardcoded)
            ctrl.helpMetadataSearchUrl = '/help/metadata-search/';
            ctrl.contactUsUrl = '/contact';

            // retrieve expert_dbs json for display in tooltips
            $http.get('/api/internal/expert-dbs/').then(
                function(response) {
                    ctrl.expertDbs = response.data;

                    // expertDbsObject has lowerCase db names as keys
                    ctrl.expertDbsObject = {};
                    for (var i=0; i < ctrl.expertDbs.length; i++) {
                        ctrl.expertDbsObject[ctrl.expertDbs[i].name.toLowerCase()] = ctrl.expertDbs[i];
                    }
                },
                function(response) {
                    ctrl.status = 'error';
                }
            );

        };

        ctrl.$doCheck = function() {
            if (search.status === 'initiating') {
                search.promise.then(
                    function() {
                        ctrl.result = search.result;
                        ctrl.status = search.status;
                    },
                    function() {
                        ctrl.result = search.result;
                        ctrl.status = search.status;
                    }
                );

                ctrl.status = search.status = 'in progress';
            }
        };

        /**
         * Fired when "Load more" button is clicked.
         */
        ctrl.loadMoreResults = function() {
            search.loadMoreResults();
        };

        /**
         * Determine if the facet has already been applied.
         */
        ctrl.isFacetApplied = function(facetId, facetValue) {
            var query = $location.search().q || '';
            var facetQuery = new RegExp(facetId + '\\:"' + facetValue + '"', 'i');
            return !!query.match(facetQuery);
        };

        /**
         * Run a search with a facet enabled.
         * The facet will be toggled on and off in the repeated calls with the same
         * parameters.
         */
        ctrl.facetSearch = function(facetId, facetValue) {
            var query = $location.search().q || '',
                facet = facetId + ':"' + facetValue + '"',
                newQuery;

            if (ctrl.isFacetApplied(facetId, facetValue)) {
                newQuery = query;

                // remove facet in different contexts
                newQuery = newQuery.replace(' AND ' + facet + ' AND ', ' AND ', 'i');
                newQuery = newQuery.replace(facet + ' AND ', '', 'i');
                newQuery = newQuery.replace(' AND ' + facet, '', 'i');
                newQuery = newQuery.replace(facet, '', 'i') || 'RNA';
            } else {
                newQuery = query + ' AND ' + facet; // add new facet
            }

            $location.search('q', newQuery);
            search.search(newQuery);
        };

        /**
         * Show/hide search facets to save screen space.
         * Uses jQuery for simplicity.
         * Activated only on mobile devices.
         */
        ctrl.toggleFacets = function() {
            var facets = $('.metasearch-facets');
            facets.toggleClass('hidden-xs', !facets.hasClass('hidden-xs'));
            $('#toggle-facets').text(function(i, text) {
                 return text === "Show facets" ? "Hide facets" : "Show facets";
            });
        };

        /**
         * Launch results export.
         * - submit export job
         * - open the results page in a new window.
         */
        ctrl.exportResults = function(format) {
            var submitQueryUrl = '/export/submit-query',
                resultsPageUrl = '/export/results';

            ctrl.showExportError = false;

            $http.get(submitQueryUrl + '?q=' + ctrl.result._query + '&format=' + format).then(
                function(response) {
                    window.location.href = resultsPageUrl + '?job=' + response.data.job_id;
                },
                function(response) {
                    ctrl.showExportError = true;
                }
            );
        };
    }]
};


var metadataSearchBar = {
    bindings: {},
    templateUrl: '/static/js/search/metadata-search-bar.html',
    controller: ['$interpolate', '$location', '$window', '$timeout', 'search', function($interpolate, $location, $window, $timeout, search) {
        var ctrl = this;
        ctrl.search = search;

        ctrl.$onInit = function() {
            ctrl.query = {
                text: '',
                submitted: false
            };

            // Check if the url contains a query when the controller is first created and initiate a search if necessary.
            if ($location.url().indexOf("/search?q=") > -1) {
                // a search result page, launch a new search
                ctrl.query.text = $location.search().q;
                search.search($location.search().q);
            }
        };

        /**
         * Called when user changes the value in query string
         */
        ctrl.autocomplete = function() {
            return search.autocomplete(ctrl.query.text).then(
                function(response) {
                    return response.data.suggestions;
                },
                function(response) {
                    return [];
                }
            );
        };

        /**
         * Called when the form is submitted, or when a link is pressed.
         *
         * @param {String} query - you can pass a query string, otherwise query string is taken from form input
         */
        ctrl.submitQuery = function(query) {
            // if query is not given and form value is invalid, die
            if (!query && ctrl.queryForm.text.$invalid) return;

            if (!query) {
                query = ctrl.query.text;
            } else {
                ctrl.query.text = query;
            }

            // set query status and location in url bar
            ctrl.query.submitted = true;
            $location.url('/search' + '?q=' + query);
            search.search(query);
        };
    }]
};


/**
 * Custom filter for inserting HTML code in templates.
 * Used for processing search results highlighting.
 */
var sanitize = function($sce) {
  return function(htmlCode){
    return $sce.trustAsHtml(htmlCode);
  }
};

/**
 * Create RNAcentral app.
 */
angular.module('rnacentralApp', ['ngAnimate', 'ui.bootstrap', 'chieffancypants.loadingBar', 'underscore', 'Genoverse'])
    .service('search', ['_', '$http', '$interpolate', '$location', '$window', search])
    .controller('MainContent', ['$scope', '$anchorScroll', '$location', 'search', MainContent])
    .component('metadataSearchResults', metadataSearchResults)
    .component('metadataSearchBar', metadataSearchBar)
    .filter("sanitize", ['$sce', sanitize])
    .config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
        // hide spinning wheel
        cfpLoadingBarProvider.includeSpinner = false;
    }])
    .config(['$locationProvider', function($locationProvider) {
        /**
         * Turn on html5mode only in modern browsers because
         * in the older ones html5mode rewrites urls with Hangbangs
         * which break normal Django pages.
         *
         * With html5mode off IE lt 10 will be able to navigate the site
         * but won't be able to open deep links to Angular pages
         * (for example, a link to a search result won't load in IE 9).
         *
         * Even in newer browsers we shall disable rewriteLinks, unless
         * we want to create a client-side router.
         */
        if (window.history && window.history.pushState) {
            $locationProvider.html5Mode({enabled: true, rewriteLinks: false});
        }

        // IE10- don't have window.location.origin, let's shim it
        if (!window.location.origin) {
             window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
        }
    }]);