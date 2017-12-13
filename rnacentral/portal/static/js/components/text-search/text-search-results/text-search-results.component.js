var textSearchResults = {
    bindings: {},
    templateUrl: '/static/js/components/text-search/text-search-results/text-search-results.html',
    controller: ['$interpolate', '$location', '$http', '$timeout', '$scope', 'search', 'routes', function($interpolate, $location, $http, $timeout, $scope, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // expose search service in template
            ctrl.search = search;

            // error flags for UI state
            ctrl.showExportError = false;
            ctrl.showExpertDbError = false;

            // urls used in template (hardcoded)
            ctrl.routes = routes;

            // slider that allows users to set range of sequence lengths
            ctrl.lengthSlider = {
                min: 1,
                max: 2147483647, // macrocosm constant; if length exceeds this, EBI search fails
                options: {
                    floor: 1,
                    ceil: 2147483647,
                    logScale: true,
                    onStart: ctrl.rememberLengthRange,
                    onEnd: ctrl.lengthSearch
                }
            };

            // retrieve expert_dbs json for display in tooltips
            $http.get(routes.expertDbsApi({ expertDbName: '' })).then(
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

            // $scope.$watch(function() { return search.result }, function(newValue, oldValue) {
            //     if (newValue !== oldValue && newValue) {
            //         console.log(newValue);
            //
            //         ctrl.lengthSlider = {
            //             min: 1,
            //             max: ctrl.search.result.fields['length'],
            //             options: {
            //                 floor: 1,
            //                 ceil: ctrl.search.result.fields['length'],
            //                 logScale: true,
            //                 // showTicks: true
            //             }
            //         };
            //     }
            // })
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
            var newQuery, facet;

            if (facetId !== 'length') {
                facet = facetId + ':"' + facetValue + '"';

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
            } else {
                facet = facetId + ':' + ctrl.oldLengthRange;
                newQuery = search.query;

                // remove length facet in different contexts
                newQuery = newQuery.replace(' AND ' + facet + ' AND ', ' AND ', 'i');
                newQuery = newQuery.replace(facet + ' AND ', '', 'i');
                newQuery = newQuery.replace(' AND ' + facet, '', 'i');
                newQuery = newQuery.replace(facet, '', 'i') || 'RNA';

                // add length facet
                facet = facetId + ':' + facetValue;
                newQuery = newQuery + ' AND ' + facet; // add new facet
            }

            search.search(newQuery);
        };

        /**
         * Edge case of facet search with length slider.
         */
        ctrl.lengthSearch = function () {
            ctrl.facetSearch('length', '[' + ctrl.lengthSlider.min + ' to ' + ctrl.lengthSlider.max + ']', true)
        };

        ctrl.rememberLengthRange = function() {
            ctrl.oldLengthRange = '[' + ctrl.lengthSlider.min + ' to ' + ctrl.lengthSlider.max + ']';
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

            // if facets were hidden, this is required to render the slider
            $timeout(function () { $scope.$broadcast('rzSliderForceRender'); });

        };

        /**
         * Launch results export.
         * - submit export job
         * - open the results page in a new window.
         */
        ctrl.exportResults = function(format) {
            $http.get(ctrl.routes.submitQuery() + '?q=' + ctrl.search.result._query + '&format=' + format).then(
                function(response) {
                    ctrl.showExportError = false;
                    window.location.href = ctrl.routes.resultsPage() + '?job=' + response.data.job_id;
                },
                function(response) {
                    ctrl.showExportError = true;
                }
            );
        };

        /*
        ctrl.expert_db_logo = function(expert_db) {
            // expert_db can contain some html markup - strip it off, replace whitespaces with hyphens
            expert_db = expert_db.replace(/\s/g, '-').toLowerCase();

            return '/static/img/expert-db-logos/' + expert_db + '.png';
        };
        */

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

angular.module('rnacentralApp').component('textSearchResults', textSearchResults);
