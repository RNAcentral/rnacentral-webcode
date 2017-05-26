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
var search = function($location) {
    /**
     * To launch a new search, change browser url,
     * which will automatically trigger a new search
     * since the url changes are watched in the query controller.
     */
    this.meta_search = function(query) {
        $location.url('/search' + '?q=' + query);
    };

};

/**
 * Service for passing data between controllers.
 */
var results = function(_, $http, $interpolate, $location, $window) {

    /**
     * Service initialization.
     */
    var result = {
        hitCount: null,
        entries: [],
        facets: [],
        _query: null, // query after preprocessing
    };

    var status = {
        display_search_interface: false, // hide results section at first
        search_in_progress: false, // display spinning wheel while searching
        show_error: false, // display error message
    };

    var search_config = {
        ebeye_base_url: global_settings.EBI_SEARCH_ENDPOINT,
        rnacentral_base_url: window.location.origin, // e.g. http://localhost:8000 or http://rnacentral.org
        fields: ['description', 'active', 'length', 'pub_title', 'has_genomic_coordinates'],
        facetfields: ['rna_type', 'TAXONOMY', 'expert_db', 'has_genomic_coordinates', 'popular_species'], // will be displayed in this order
        facetcount: 30,
        pagesize: 15,
    };

    var query_urls = {
        'ebeye_search': search_config.ebeye_base_url +
                        '?query={{ query }}' +
                        '&format=json' +
                        '&hlfields=' + search_config.fields.join() +
                        '&facetcount=' + search_config.facetcount +
                        '&facetfields=' + search_config.facetfields.join() +
                        '&size=' + search_config.pagesize +
                        '&start={{ start }}' +
                        '&sort=boost:descending,length:descending' +
                        '&hlpretag=<span class=metasearch-highlights>&hlposttag=</span>',
        'ebeye_autocomplete': 'http://www.ebi.ac.uk/ebisearch/ws/RNAcentral/autocomplete' +
                              '?term={{ input }}' +
                              '&format=json',
        'proxy': search_config.rnacentral_base_url +
                 '/api/internal/ebeye?url={{ ebeye_url }}',
    };

    /**
     * Launch EBeye search.
     * `start` determines the range of the results to be returned.
     */
    this.search = function(query, start) {
        start = start || 0;

        hopscotch.endTour(); // end guided tour when a search is launched

        // setting display_search_interface to true hides non-search-related content and shows search results
        status.display_search_interface = true;

        // display search spinner if not a "load more" request
        if (start === 0) result.hitCount = null;

        // change page title, which is also used in browser tabs
        $window.document.title = 'Search: ' + query;

        query = preprocess_query(query);

        // get query_url ready
        var ebeye_url = $interpolate(query_urls.ebeye_search)({query: query, start: start});
        var query_url = $interpolate(query_urls.proxy)({ebeye_url: encodeURIComponent(ebeye_url)});

        execute_ebeye_search(query_url, start === 0);

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

            // replace URS/taxid with URS_taxid - replace slashes with underscore
            query = query.replace(/(URS[0-9A-F]{10})\/(\d+)/ig, '$1_$2');

            // replace length query with a placeholder, example: length:[100 TO 200]
            var length_clause = query.match(/length\:\[\d+\s+to\s+\d+\]/i);
            var placeholder = 'length_clause';
            if (length_clause) {
              query = query.replace(length_clause[0], placeholder);
              length_clause[0] = length_clause[0].replace(/to/i, 'TO');
            }

            var words = query.match(/[^\s"]+|"[^"]*"/g);
            var array_length = words.length;
            for (var i = 0; i < array_length; i++) {
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
                    words[i] = escape_search_term(words[i]);
                } else if ( words[i].match(/^".+?"$/) ) {
                    // double quotes, do nothing
                } else if ( words[i].match(/\*$/) ) {
                    // wildcard, escape term
                    words[i] = escape_search_term(words[i]);
                } else if ( words[i].match(/\)$/) ) {
                    // right closing grouping parenthesis, don't add a wildcard
                } else if ( words[i].length < 3 ) {
                    // the word is too short for wildcards, do nothing
                } else {
                    // all other words
                    // escape term, add wildcard
                    words[i] = escape_search_term(words[i]) + '*';
                }
            }
            query = words.join(' ');
            query = query.replace(/\: /g, ':'); // to avoid spaces after faceted search terms
            // replace placeholder with the original search term
            if (length_clause) {
              query = query.replace(placeholder + '*', length_clause[0]);
            }
            result._query = query;
            return query;

            /**
             * Escape special symbols used by Lucene
             * Escaped: + - && || ! { } [ ] ^ ~ ? : \ /
             * Not escaped: * " ( ) because they may be used deliberately by the user
             */
            function escape_search_term(search_term) {
                return search_term.replace(/[\+\-&|!\{\}\[\]\^~\?\:\\\/]/g, "\\$&");
            }
        }

        /**
         * Execute remote request.
         */
        function execute_ebeye_search(url, overwrite_results) {
            status.search_in_progress = true;
            status.show_error = false;
            $http.get(url, params).then(
                function(response) {
                    data = preprocess_results(response.data);
                    overwrite_results = overwrite_results || false;
                    if (overwrite_results) {
                        data._query = result._query;
                        result = data; // replace
                    } else {
                        // append new entries
                        result.entries = result.entries.concat(data.entries);
                    }
                    status.search_in_progress = false;
                },
                function(response) {
                    status.search_in_progress = false;
                    status.show_error = true;
                }
            );

            /**
             * Preprocess data received from the server.
             */
            function preprocess_results(data) {

                merge_species_facets();
                order_facets();
                rename_hlfields();
                return data;

                /**
                 * Use `hlfields` with highlighted matches instead of `fields`.
                 */
                function rename_hlfields() {
                    for (var i=0; i < data.entries.length; i++) {
                        data.entries[i].fields = data.entries[i].highlights;
                        data.entries[i].fields.length[0] = data.entries[i].fields.length[0].replace(/<[^>]+>/gm, '');
                        data.entries[i].id_with_slash = data.entries[i].id.replace('_', '/');
                    }
                }

                /**
                 * Order facets the same way as in the config.
                 */
                function order_facets() {
                    data.facets = _.sortBy(data.facets, function(facet){
                        return _.indexOf(search_config.facetfields, facet.id);
                    });
                }

                /**
                 * Merge the two species facets putting popular_species
                 * at the top of the list.
                 * Species facets:
                 * - TAXONOMY (all species)
                 * - popular_species (manually curated set of top organisms).
                 */
                function merge_species_facets() {

                    // find the popular species facet
                    var top_species_facet_id = find_facet_id('popular_species');

                    if (top_species_facet_id) {
                        // get top species names
                        var popular_species = _.pluck(data.facets[top_species_facet_id].facetValues, 'label');

                        // find the taxonomy facet
                        var taxonomy_facet_id = find_facet_id('TAXONOMY');

                        // extract other species from the taxonomy facet
                        var other_species = get_other_species();

                        // merge popular_species with other_species
                        data.facets[taxonomy_facet_id].facetValues = data.facets[top_species_facet_id].facetValues.concat(other_species);

                        // remove the Popular species facet
                        delete data.facets[top_species_facet_id];
                        data.facets = _.compact(data.facets);
                    }

                    /**
                     * Get Taxonomy facet values that are not also in popular_species.
                     */
                    function get_other_species() {
                        var taxonomy_facet = data.facets[taxonomy_facet_id].facetValues,
                            other_species = [];
                        for (var i=0; i<taxonomy_facet.length; i++) {
                            if (_.indexOf(popular_species, taxonomy_facet[i].label) === -1) {
                                other_species.push(taxonomy_facet[i]);
                            }
                        }
                        return other_species;
                    }

                    /**
                     * Find objects in array by attribute value.
                     * Given an array like:
                     * [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
                     * find_facet_id('b') -> 1
                     */
                    function find_facet_id(facet_label) {
                        var index;
                        _.find(data.facets, function(facet, i){
                            if (facet.id === facet_label) {
                                index = i;
                                return true;
                            }
                        });
                        return index;
                    }
                }

            }
        }

    };

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

};

var MainContent = function($scope, $anchorScroll, $location, results, search) {
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
        if (newValue !== null) {
            $scope.display_search_interface = newValue;
        }
    });

    /**
     * Launch a metadata search from a web page.
     */
    $scope.meta_search = function(query) {
        search.meta_search(query);
    };
};

/**
 * Results display controller
 * Responsible for visualising search results.
 */
var metadataSearchResults = {
    bindings: {},
    templateUrl: '/static/js/search/metadata-search-results.html',
    controller: ['$location', '$http', 'results', function($location, $http, results) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.result = { entries: [] };
            ctrl.show_export_error = false;
            ctrl.search_in_progress = results.get_search_in_progress();
            ctrl.show_error = results.get_show_error();

            $http.get('/api/internal/expert-dbs/').then(function(response) {
                ctrl.expertDbs = response.data;

                // expertDbsObject has lowerCase db names as keys
                ctrl.expertDbsObject = {};
                for (var i=0; i < ctrl.expertDbs.length; i++) {
                    ctrl.expertDbsObject[ctrl.expertDbs[i].name.toLowerCase()] = ctrl.expertDbs[i];
                }
            });
        };

        ctrl.$doCheck = function() {
            if (results.get_result() !== null) ctrl.result = results.get_result();
            if (results.get_status() !== null) ctrl.display_search_interface = results.get_status();
            if (results.get_search_in_progress() !== ctrl.search_in_progress) ctrl.search_in_progress = results.get_search_in_progress();
            if (results.get_show_error() !== ctrl.show_error) ctrl.show_error = results.get_show_error();
        };

        /**
         * Fired when "Load more" button is clicked.
         */
        ctrl.load_more_results = function() {
            results.load_more_results();
        };

        /**
         * Determine if the facet has already been applied.
         */
        ctrl.is_facet_applied = function(facet_id, facet_value) {
            var query = $location.search().q || '';
            var facet_query = new RegExp(facet_id + '\\:"' + facet_value + '"', 'i');
            return !!query.match(facet_query);
        };

        /**
         * Run a search with a facet enabled.
         * The facet will be toggled on and off in the repeated calls with the same
         * parameters.
         */
        ctrl.facet_search = function(facet_id, facet_value) {
            var query = $location.search().q || '',
                facet = facet_id + ':"' + facet_value + '"',
                new_query;

            if (ctrl.is_facet_applied(facet_id, facet_value)) {
                new_query = query;

                // remove facet in different contexts
                new_query = new_query.replace(' AND ' + facet + ' AND ', ' AND ', 'i');
                new_query = new_query.replace(facet + ' AND ', '', 'i');
                new_query = new_query.replace(' AND ' + facet, '', 'i');
                new_query = new_query.replace(facet, '', 'i') || 'RNA';
            } else {
                new_query = query + ' AND ' + facet; // add new facet
            }
            $location.search('q', new_query);
        };

        /**
         * Show/hide search facets to save screen space.
         * Uses jQuery for simplicity.
         * Activated only on mobile devices.
         */
        ctrl.toggle_facets = function() {
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
        ctrl.export_results = function(format) {
            var submit_query_url = '/export/submit-query',
                results_page_url = '/export/results';

            ctrl.show_export_error = false;

            $http.get(submit_query_url + '?q=' + ctrl.result._query + '&format=' + format).then(
                function(response) {
                    window.location.href = results_page_url + '?job=' + response.data.job_id;
                },
                function(response) {
                    ctrl.show_export_error = true;
                }
            );
        };
    }]
};



var metadataSearchBar = {
    bindings: {},
    templateUrl: '/static/js/search/metadata-search-bar.html',
    controller: ['$interpolate', '$location', '$window', '$timeout', 'results', 'search', function($interpolate, $location, $window, $timeout, results, search) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.query = {
                text: '',
                submitted: false
            };

            // Check if the url contains a query when the controller is first created and initiate a search if necessary.
            if ($location.url().indexOf("/search?q=") > -1) {
                // a search result page, launch a new search
                ctrl.query.text = $location.search().q;
                results.search($location.search().q);
            }
        };

        /**
         * Launch a metadata search using the service.
         */
        ctrl.meta_search = function(query) {
            search.meta_search(query);
        };

        /**
         * Called when user changes the value in query string
         */
        ctrl.autocomplete = function(input) {
            // get query_url ready
            var ebeye_url = $interpolate(query_urls.ebeye_autocomplete)({input: input});
            var query_url = $interpolate(query_urls.proxy)({ebeye_url: encodeURIComponent(ebeye_url)});

            return $http.get($interpolate(query_url)(input));
        };

        /**
         * Called when the form is submitted.
         */
        ctrl.submit_query = function() {
            ctrl.query.submitted = true;
            if (ctrl.queryForm.text.$invalid) {
                return;
            }
            ctrl.meta_search(ctrl.query.text);
        };

        // /**
        //  * Control browser navigation buttons.
        //  */
        // $scope.$watch($location.url, function (newUrl, oldUrl) {
        //     // ignore url hash
        //     newUrl = newUrl.replace(/#.+$/, '');
        //     oldUrl = oldUrl.replace(/#.+$/, '');
        //
        //     // url has changed
        //     if (newUrl !== oldUrl) {
        //         if (newUrl.indexOf('tab=') !== -1) {
        //             // redirect only if the main part of url has changed
        //             if (newUrl.split('?')[0] !== oldUrl.split('?')[0]) {
        //                 redirect(newUrl);
        //             }
        //             else { // navigate page tabs using browser back button
        //                 matches = newUrl.match(/tab=(\w+)&?/);
        //                 $('#tabs a[data-target="#' + matches[1] + '"]').tab('show');
        //             }
        //         }
        //
        //         else if (newUrl.indexOf('xref-filter') !== -1) {
        //             if (newUrl.split('?')[0] !== oldUrl.split('?')[0]) {
        //                 redirect(newUrl);
        //             }
        //         }
        //
        //         // let the sequence search app handle it
        //         else if (oldUrl.indexOf('sequence-search') !== -1 && newUrl.indexOf('sequence-search') !== -1) {}
        //
        //         // let genome-browser handle its own transitions
        //         else if (oldUrl.indexOf('genome-browser') !== -1 && newUrl.indexOf('genome-browser') !== -1) {}
        //
        //         // a non-search url, load that page
        //         else if (newUrl.indexOf('/search') == -1) {
        //             redirect(newUrl);
        //         }
        //
        //         // the new url is a search result page, launch that search
        //         else {
        //             $scope.query.text = $location.search().q;
        //             results.search($location.search().q);
        //             $scope.query.submitted = false;
        //         }
        //     }
        //
        //     function redirect(newUrl) {
        //         $timeout(function() {
        //             // wrapping in $timeout to avoid "digest in progress" errors
        //             $window.location = newUrl;
        //         });
        //     }
        //
        // });
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
    .service('search', ['$location', search])
    .service('results', ['_', '$http', '$interpolate', '$location', '$window', results])
    .controller('MainContent', ['$scope', '$anchorScroll', '$location', 'results', 'search', MainContent])
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
         * With html5mode off IE lt 10 will be able to navigate the site
         * but won't be able to open deep links to Angular pages
         * (for example, a link to a search result won't load in IE 9).
         */
        if (window.history && window.history.pushState) {
            $locationProvider.html5Mode(true);
        }

        // IE10- don't have window.location.origin, let's shim it
        if (!window.location.origin) {
             window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
        }
    }]);