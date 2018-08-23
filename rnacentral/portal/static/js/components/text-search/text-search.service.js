/**
 * Service for launching a text search.
 */

var search = function (_, $http, $interpolate, $location, $window, $q, routes) {
    var self = this; // in case some event handler or constructor overrides "this"

    this.config = {
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
            'rfam_problem_found',
            'rfam_problems',
            'rna_type',
            'standard_name',
            'tax_string'
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
            'standard_name': 2,
            'tax_string': 2,
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
            'standard_name': 'Standard name',
            'tax_string': 'Taxonomy'
        },
        facetfields: ['length', 'rna_type', 'TAXONOMY', 'expert_db', 'rfam_problem_found', 'has_genomic_coordinates', 'popular_species'], // will be displayed in this order
        sortableFields: [
            { label: 'Popular species, Length ↓', value: 'boost:descending,length:descending' },
            // { label: 'Popular species ↑', value: 'boost:ascending' },
            { label: 'Length ↓', value: 'length:descending' },
            { label: 'Length ↑', value: 'length:ascending' },
            // { label: 'Citations number ↓', value: 'n_citations:descending' },
            // { label: 'Citations number ↑', value: 'n_citations:ascending' },
            // { label: 'Annotations number ↓', value: 'n_xrefs:descending' },
            // { label: 'Annotations number ↑', value: 'n_xrefs:ascending' }
        ],
        facetcount: 30,
        pagesize: 15,
    };

    /**
     * Service initialization.
     */
    this.result = {
        hitCount: null,
        entries: [],
        facets: []
    };

    this.status = 'off'; // possible values: 'off', 'in progress', 'success', 'error'

    this.query = ''; // the query will be observed by watches
    this.sort = 'boost:descending,length:descending' // EBI search endpoint sorts results by this field value
    this.sortTiebreaker = 'length:descending'; // secondary search field, used in case first field is even

    this.callbacks = []; // callbacks to be called after each search.search(); done for slider redraw

    /**
     * Launch EBeye autocompletion.
     *
     * Note that we're using $q CommonJS deferred syntax here,
     * not simpler ES6-ish, cause we need to cancel autocomplete request,
     * if search is started, which is not possible with ES6.
     *
     * @param query
     * @returns {Promise}
     */
    this.autocomplete = function (query) {
        self = this;

        self.autocompleteDeferred = $q.defer();

        if (query.length < 3) {
            self.autocompleteDeferred.reject("query too short!");
        }
        else {
            // get queryUrl ready
            var ebeyeUrl = routes.ebiAutocomplete({query: query});
            var queryUrl = routes.ebiSearchProxy({ebeyeUrl: encodeURIComponent(ebeyeUrl)});

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
     * For length slider we need to do updates after each search.
     * @param callback - function to be called after every successful search
     */
    this.registerSearchCallback = function (callback) {
        this.callbacks.push(callback);
    };

    /**
     * Launch EBeye search.
     * @param query
     * @param start - determines the range of the results to be returned.
     * @creates self.promise
     */
    this.search = function (query, start) {
        start = start || 0;

        // hopscotch.endTour(); // end guided tour when a search is launched
        self.autocompleteDeferred && self.autocompleteDeferred.reject(); // if autocompletion was launched - reject it

        self.query = query;
        self.status = 'in progress';

        // display search spinner if not a "load more" request
        if (start === 0) self.result.hitCount = null;

        // change page title, which is also used in browser tabs
        $window.document.title = 'Search: ' + query;

        query = self.preprocessQuery(query);

        // get queryUrl ready
        var ebeyeUrl = routes.ebiSearch({
            ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT,
            query: query,
            hlfields: self.config.fields.join(),
            facetcount: self.config.facetcount,
            facetfields: self.config.facetfields.join(),
            size: self.config.pagesize,
            start: start,
            sort: self.sort
        });
        var queryUrl = routes.ebiSearchProxy({ebeyeUrl: encodeURIComponent(ebeyeUrl)});

        // perform search
        var overwriteResults = (start === 0);

        self.promise = $http.get(queryUrl).then(
            function(response) {
                var data = self.preprocessResults(response.data);

                overwriteResults = overwriteResults || false;
                if (overwriteResults) {
                    self.result = data; // replace
                } else {
                    self.result.entries = self.result.entries.concat(data.entries); // append new entries
                }

                // after each search send a pageview to GA
                $window.ga('send', 'pageview', $location.path());
                self.status = 'success';

                // run callbacks
                self.callbacks.forEach(function(callback) { callback() });
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
    this.preprocessQuery = function (query) {

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
        return query;

        /**
         * Escape special symbols used by Lucene
         * Escaped: + - && || ! { } [ ] ^ ~ ? : \ /
         * Not escaped: * " ( ) because they may be used deliberately by the user
         */
        function escapeSearchTerm (searchTerm) {
            return searchTerm.replace(/[\+\-&|!\{\}\[\]\^~\?\:\\\/]/g, "\\$&");
        }
    };

    // /**
    //  * Looks into self.sort (e.g. [['boost', 'ascending'], ['length', 'descending']])
    //  * @returns {string} - e.g. 'boost:ascending,length:descending'
    //  */
    // this.preprocessSort = function () {
    //     var sort = "";
    //     self.sort.forEach( function (field) { sort.concat("," + field[0] + ":" + field[1]) } );
    //     return sort;
    // };

    /**
     * Preprocess data received from the server.
     */
    this.preprocessResults = function (data) {

        _mergeSpeciesFacets(data);

        // order facets the same way as in the config
        data.facets = _.sortBy(data.facets, function(facet){
            return _.indexOf(self.config.facetfields, facet.id);
        });

        // update rfam_problem_found labels from True/Fase to Yes/No
        for (var i=0; i < data.facets.length; i++) {
            if (data.facets[i].id == 'rfam_problem_found') {
                for (var j=0; j < data.facets[i].facetValues.length; j++) {
                    if (data.facets[i].facetValues[j].label == 'True') {
                        data.facets[i].facetValues[j].label = 'Yes';
                    } else if (data.facets[i].facetValues[j].label == 'False') {
                        data.facets[i].facetValues[j].label = 'No';
                    }
                }
            }
        }

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
        function _mergeSpeciesFacets (data) {

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
            function _findFacetId (facetLabel, data) {
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
            function _getOtherSpecies (data) {
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
    this.loadMoreResults = function () {
        self.search(self.query, self.result.entries.length);
    };

    /**
     * Checks, if search query contains any lucene-specific syntax, or if it's a plain text
     */
    this.luceneSyntaxUsed = function (query) {
        if (/[\+\-\&\|\!\{\}\[\]\^~\?\:\\\/\*\"\(]/.test(query)) return true;
        if (/[\s\"]OR[\s\"]/.test(query)) return true;
        if (/[\s\"]AND[\s\"]/.test(query)) return true;
        return false;
    }
};

angular.module('textSearch')
    .service('search', ['_', '$http', '$interpolate', '$location', '$window', '$q', 'routes', search]);
