var textSearchResults = {
    bindings: {},
    templateUrl: '/static/js/components/text-search/text-search-results/text-search-results.html',
    controller: ['$location', '$http', 'search', 'routes', function($location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // expose search service in template
            ctrl.search = search;

            // error flags for UI state
            ctrl.showExportError = false;
            ctrl.showExpertDbError = false;

            // urls used in template (hardcoded)
            ctrl.routes = routes;

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
            $http.get(ctrl.routes.submitQuery + '?q=' + ctrl.search.result._query + '&format=' + format).then(
                function(response) {
                    ctrl.showExportError = false;
                    window.location.href = ctrl.routes.resultsPage + '?job=' + response.data.job_id;
                },
                function(response) {
                    ctrl.showExportError = true;
                }
            );
        };
    }]
};