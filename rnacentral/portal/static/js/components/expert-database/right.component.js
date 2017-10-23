var right = {
    bindings: {
        onError: "&",
        expertDb : "<"
    },
    templateUrl: '/static/js/components/expert-database/right.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', function($interpolate, $location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // variables
            ctrl.routes = routes;  // urls used in template (hardcoded)
            ctrl.noSunburst = ['ena', 'rfam', 'silva', 'greengenes'];  // don't show sunburst for these databases
            ctrl.expertDbStats = null;

            // retrieve databaseStats from server, render them, if success
            $http.get(routes.expertDbStatsApi({expertDbName: ctrl.expertDb.label.toUpperCase()})).then(
                function(response) {
                    ctrl.expertDbStats = response.data;

                    if (ctrl.expertDb.label != 'lncrnadb') {
                        ExpertDatabaseSequenceDistribution(
                            "#d3-seq-length-distribution",
                            ctrl.expertDbStats.length_counts,
                            500,
                            300,
                            routes.textSearch()
                        );
                    }

                    if (ctrl.noSunburst.indexOf(ctrl.expertDb.label) === -1) {
                        d3SpeciesSunburst(ctrl.expertDbStats.taxonomic_lineage, '#d3-species-sunburst', 500, 300);
                    }
                },
                function(response) {
                    console.log("received an error");
                    ctrl.onError();
                }
            );
        };
    }]
};

angular.module('expertDatabase').component('right', right);