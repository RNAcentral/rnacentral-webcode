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
 * RNAcentral text search Angular.js app.
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
 * Service for launching a text search.
 */

var search = function(_, $http, $interpolate, $location, $window, $q) {
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

    this.status = 'off'; // possible values: 'off', 'in progress', 'success', 'error'

    this.query = ''; // the query will be observed by watches

    this.config = {
        ebeyeBaseUrl: global_settings.EBI_SEARCH_ENDPOINT,
        rnacentralBaseUrl: window.location.origin, // e.g. http://localhost:8000 or http://rnacentral.org
        fields: [
            'active',
            'author',
            'common_name',
            'description',
            'expert_db',
            'function',
            'gene',
            'gene_synonym',
            'has_genomic_coordinates',
            'length',
            'locus_tag',
            'organelle',
            'pub_title',
            'product',
            'rna_type',
            'standard_name'
        ],
        fieldWeights: {
            'active': 0,
            'author': 2,
            'common_name': 3,
            'description': 2,
            'expert_db': 4,
            'function': 4,
            'gene': 4,
            'gene_synonym': 3,
            'has_genomic_coordinates': 0,
            'length': 0,
            'locus_tag': 2,
            'organelle': 3,
            'pub_title': 2,
            'product': 1,
            'rna_type': 2,
            'standard_name': 2
        },
        fieldVerboseNames: {
            'active': 'Active',
            'author': 'Author',
            'common_name': 'Species',
            'description': 'Description',
            'expert_db': 'Source',
            'function': 'Function',
            'gene': 'Gene',
            'gene_synonym': 'Gene synonym',
            'has_genomic_coordinates': 'Genomic coordinates',
            'locus_tag': 'Locus tag',
            'length': 'Length',
            'organelle': 'Organelle',
            'pub_title': 'Publication title',
            'product': 'Product',
            'rna_type': 'RNA type',
            'standard_name': 'Standard name'
        },
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
                        '&hlpretag=<span class=text-search-highlights>' +
                        '&hlposttag=</span>',
        'ebeyeAutocomplete': 'http://www.ebi.ac.uk/ebisearch/ws/rest/RNAcentral/autocomplete' +
                              '?term={{ query }}' +


                              '&format=json',
        'proxy': self.config.rnacentralBaseUrl +
                 '/api/internal/ebeye?url={{ ebeyeUrl }}',
    };

    this.autocomplete = function(query) {
        self = this;
        self.autocompleteDeferred = $q.defer();

        if (query.length < 3) {
            self.autocompleteDeferred.reject("query too short!");
        }
        else {
            // get queryUrl ready
            var ebeyeUrl = $interpolate(self.queryUrls.ebeyeAutocomplete)({query: query});
            var queryUrl = $interpolate(self.queryUrls.proxy)({ebeyeUrl: encodeURIComponent(ebeyeUrl)});

            $http.get(queryUrl, {ignoreLoadingBar: true}).then(
                function(response) {
                    self.autocompleteDeferred.resolve(response);
                },
                function(response) {
                    self.autocompleteDeferred.reject(response);
                }
            );
        }

        return self.autocompleteDeferred.promise;
    };

    /**
     * Launch EBeye search.
     * `start` determines the range of the results to be returned.
     */
    this.search = function(query, start) {
        start = start || 0;

        hopscotch.endTour(); // end guided tour when a search is launched
        self.autocompleteDeferred && self.autocompleteDeferred.reject(); // if autocompletion was launched - reject it

        self.query = query;
        self.status = 'in progress';

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
                $window.ga('send', 'pageview', $location.path());
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
        self.search(self.query, self.result.entries.length);
    };

    /**
     * Checks, if search query contains any lucene-specific syntax, or if it's a plain text
     */
    this.luceneSyntaxUsed = function(query) {
        if (/[\+\-\&\|\!\{\}\[\]\^~\?\:\\\/\*\"\(]/.test(query)) return true;
        if (/[\s\"]OR[\s\"]/.test(query)) return true;
        if (/[\s\"]AND[\s\"]/.test(query)) return true;
        return false;
    }
};

var MainContent = function($scope, $anchorScroll, $location, search) {
    $scope.displaySearchInterface = false;
    $scope.search = search; // expose search service to templates

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

    /**
     * Watch query and if it changes, modify url accordingly.
     */
    $scope.$watch(function() { return search.query; }, function(newValue, oldValue) {
        if (newValue != oldValue && newValue) {
            $location.url('/search' + '?q=' + search.query);
        }
    });
};


var textSearchResults = {
    bindings: {},
    templateUrl: '/static/js/search/text-search-results.html',
    controller: ['$location', '$http', '$filter', 'search', function($location, $http, $filter, search) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // expose search service in template
            ctrl.search = search;

            // error flags for UI state
            ctrl.showExportError = false;
            ctrl.showExpertDbError = false;

            // urls used in template (hardcoded)
            ctrl.routes = {
                helpTextSearchUrl: '/help/text-search/',
                contactUsUrl: '/contact',
                submitQueryUrl: '/export/submit-query',
                resultsPageUrl: '/export/results'
            };

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
                    ctrl.showExpertDbError = true;
                }
            );
        };

        /**
         * Determine if the facet has already been applied.
         */
        ctrl.isFacetApplied = function(facetId, facetValue) {
            var facetQuery = new RegExp(facetId + '\\:"' + facetValue + '"', 'i');
            return !!search.query.match(facetQuery);
        };

        /**
         * Run a search with a facet enabled.
         * The facet will be toggled on and off in the repeated calls with the same
         * parameters.
         */
        ctrl.facetSearch = function(facetId, facetValue) {
            var newQuery;

            var facet = facetId + ':"' + facetValue + '"';
            if (ctrl.isFacetApplied(facetId, facetValue)) {
                newQuery = search.query;

                // remove facet in different contexts
                newQuery = newQuery.replace(' AND ' + facet + ' AND ', ' AND ', 'i');
                newQuery = newQuery.replace(facet + ' AND ', '', 'i');
                newQuery = newQuery.replace(' AND ' + facet, '', 'i');
                newQuery = newQuery.replace(facet, '', 'i') || 'RNA';
            } else {
                newQuery = search.query + ' AND ' + facet; // add new facet
            }

            search.search(newQuery);
        };

        /**
         * Show/hide search facets to save screen space.
         * Uses jQuery for simplicity.
         * Activated only on mobile devices.
         */
        ctrl.toggleFacets = function() {
            var facets = $('.text-search-facets');
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
            $http.get(ctrl.routes.submitQueryUrl + '?q=' + ctrl.search.result._query + '&format=' + format).then(
                function(response) {
                    ctrl.showExportError = false;
                    window.location.href = ctrl.routes.resultsPageUrl + '?job=' + response.data.job_id;
                },
                function(response) {
                    ctrl.showExportError = true;
                }
            );
        };

        ctrl.expert_db_logo = function(expert_db) {
            // expert_db can contain some html markup - strip it off, replace whitespaces with hyphens
            expert_db = expert_db.replace(/\s/g, '-').toLowerCase();

            return '/static/img/expert-db-logos/' + expert_db + '.png';
        };

        /**
         * Sorts expertDbs so that starred dbs have priority over non-starred, otherwise, keeping lexicographical order.
         * @param v1 - plaintext db name
         * @param v2 - plaintext db name
         * @returns {number} - (-1 if v1 before v2) or (1 if v1 after v2)
         */
        ctrl.expertDbHasStarComparator = function(v1, v2) {
            if (ctrl.expertDbHasStar(v1.value.toLowerCase()) && !ctrl.expertDbHasStar(v2.value.toLowerCase())) return -1;
            else if (!ctrl.expertDbHasStar(v1.value.toLowerCase()) && ctrl.expertDbHasStar(v2.value.toLowerCase())) return 1;
            else
                return v1.value.toLowerCase() < v2.value.toLowerCase() ? -1 : 1;
        };

        /**
         * We assign a star only to those expert_dbs that have a curated tag and don't have automatic tag at the same time.
         * @param db {String} - name of expert_db as a key in expertDbsObject
         * @returns {boolean}
         */
        ctrl.expertDbHasStar = function(db) {
            return ctrl.expertDbsObject[db].tags.indexOf('curated') != -1 && ctrl.expertDbsObject[db].tags.indexOf('automatic') == -1;
        };

        /**
         * Given EBIsearch results, returns a field name and a highlighted text snippet, matching the query. This
         * helps explain the user, why this result was included into the results list.
         * @param fields {Object} - object of field as returned by search.search()
         * @returns {{highlight: String, fieldName: String}}
         */
        ctrl.highlight = function(fields) {
            var highlight;
            var verboseFieldName;
            var maxWeight = -1; // multiple fields can have highlights - pick the field with highest weight

            for (var fieldName in fields) {
                if (fields.hasOwnProperty(fieldName) && ctrl.anyHighlightsInField(fields[fieldName])) { // description is quoted in hit's header, ignore it
                    if (search.config.fieldWeights[fieldName] > maxWeight) {

                        // get highlight string with match
                        var field = fields[fieldName];
                        for (var i = 0; i < fields.length; i++) {
                            if (field[i].indexOf('text-search-highlights') !== -1) {
                                highlight = field[i];
                                break;
                            }
                        }

                        // assign the new weight and verboseFieldName
                        maxWeight = search.config.fieldWeights[fieldName];
                        verboseFieldName = search.config.fieldVerboseNames[fieldName];
                    }
                }
            }

            // use human-readable fieldName
            return {highlight: highlight, fieldName: verboseFieldName};
        };

        /**
         * Are there any highlighted snippets in search results at all?
         */
        ctrl.anyHighlights = function(fields) {
            for (var fieldName in fields) {
                if (fields.hasOwnProperty(fieldName) && ctrl.anyHighlightsInField(fields[fieldName])) {
                    return true;
                }
            }
            return false;
        };

        /**
         * Does the given field contain any highlighted text snippets?
         */
        ctrl.anyHighlightsInField = function(field) {
            for (var i=0; i < field.length; i++) {
                if (field[i].indexOf('text-search-highlights') !== -1) {
                    return true;
                }
            }
            return false;
        };
    }]
};


var textSearchBar = {
    bindings: {},
    templateUrl: '/static/js/search/text-search-bar.html',
    controller: ['$interpolate', '$location', '$window', '$timeout', 'search', function($interpolate, $location, $window, $timeout, search) {
        var ctrl = this;
        ctrl.search = search;

        ctrl.$onInit = function() {
            ctrl.query = '';
            ctrl.submitted = false; // when form is submitted this flag is set; when its content is edited it is cleared

            // check if the url contains a query when the controller is first created and initiate a search if necessary
            if ($location.url().indexOf("/search?q=") > -1) {
                search.search($location.search().q); // a search result page, launch a new search
            }
        };

        /**
         * Watch search.query and if it's different from ctrl.query, check, who changed and sync if necessary
         */
        ctrl.$doCheck = function() {
            if (search.query != ctrl.query) {
                if (search.status == 'in progress') {
                    // this is a result of search.search() call => sync form input with search.query
                    ctrl.query = search.query;
                }
            }
        };

        /**
         * Called when user changes the value in query string.
         */
        ctrl.autocomplete = function(query) {
            return search.autocomplete(query).then(
                function(response) {
                    // make exact matches appear in the top of the list
                    var exactMatches = [], fuzzyMatches = [];
                    for (var i=0; i < response.data.suggestions.length; i++) {
                        var suggestion = response.data.suggestions[i].suggestion;
                        if (suggestion.indexOf(ctrl.query) === 0) exactMatches.push(suggestion);
                        else fuzzyMatches.push(suggestion);
                    }

                    return exactMatches.concat(fuzzyMatches);
                },
                function(response) {
                    return [];
                }
            );
        };

        /**
         * Called when the form is submitted. If request is invalid, just display error and die, else run search.
         */
        ctrl.submitQuery = function() {
            ctrl.queryForm.text.$invalid ? ctrl.submitted = true : search.search(ctrl.query);
        };
    }]
};


/**
 * Custom filter for inserting HTML code in templates.
 * Used for processing search results highlighting.
 */
var sanitize = function($sce) {
  return function(htmlCode) {
    return $sce.trustAsHtml(htmlCode);
  }
};

/**
 * Given an array of strings with html markup, strips
 * all the markup from those strings and leaves only the text.
 */
var plaintext = function() {
    return function(items) {
        var result = [];

        angular.forEach(items, function(stringWithHtml) {
            result.push(String(stringWithHtml).replace(/<[^>]+>/gm, ''));
        });

        return result;
    };
};
/**
 * Makes first letter of the input string captial.
 */
var capitalizeFirst = function() {
    return function(item) {
        return item.charAt(0).toUpperCase() + item.slice(1);
    };
};

/**
 * Replaced all the occurrences of underscore in the input string with period (dot) and whitespace.
 * E.g. pub_title -> pub. title.
 */
var underscoresToSpaces = function() {
    return function(item) {
        return item.replace(/_/g, ' ');
    }
}

/**
 * Create RNAcentral app.
 */
angular.module('rnacentralApp', ['ngAnimate', 'ui.bootstrap', 'chieffancypants.loadingBar', 'underscore', 'Genoverse'])
    .service('search', ['_', '$http', '$interpolate', '$location', '$window', '$q', search])
    .controller('MainContent', ['$scope', '$anchorScroll', '$location', 'search', MainContent])
    .component('textSearchResults', textSearchResults)
    .component('textSearchBar', textSearchBar)
    .filter("sanitize", ['$sce', sanitize])
    .filter("plaintext", [plaintext])
    .filter("capitalizeFirst", [capitalizeFirst])
    .filter("underscoresToSpaces", [underscoresToSpaces])
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
    }])
    .run(['$rootScope', '$window', function($rootScope, $window) {
        $window.onpopstate = function() {
            $window.location.reload();
        }
    }]);
