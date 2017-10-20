var right = {
    bindings: {
        expertDb : "<"
    },
    templateUrl: '/static/js/components/expert-database/right.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', function($interpolate, $location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // variables
            ctrl.routes = routes;  // urls used in template (hardcoded)
            ctrl.noSunburst = ['ena', 'rfam', 'silva', 'greengenes'];  // don't show sunburst for these databases

            if (ctrl.expertDb.label != 'lncrnadb') {
                var data = expert_db_stats.length_counts;
                var search_url = routes.textSearch;  // '{% url "text-search" %}';
                ExpertDatabaseSequenceDistribution("#d3-seq-length-distribution", data, 500, 300, search_url);
            }

            if ($ctrl.noSunburst.index(ctrl.expertDb.label) === -1) {
                data = expert_db_stats.taxonomic_lineage;
                d3SpeciesSunburst(data, '#d3-species-sunburst', 500, 300);
            }
        };
    }]
};

angular.module('expertDatabase').component('right', right);