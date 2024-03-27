var expertDatabaseRight = {
    bindings: {
        onError: "&",
        expertDb : "<"
    },
    templateUrl: '/static/js/components/expert-database/expert-database-right.html',
    controller: ['$http', 'search', 'routes', 'normalizeExpertDbName', function($http, search, routes, normalizeExpertDbName) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // variables
            ctrl.routes = routes;  // urls used in template (hardcoded)
            ctrl.noSunburst = ['ena', 'rfam', 'silva', 'greengenes', 'lncipedia', '5srrnadb', 'rediportal'];  // don't show sunburst for these databases
            ctrl.expertDbStats = null;

            // retrieve databaseStats from server, render them, if success
            var normalizedDbName = normalizeExpertDbName.labelToDb(ctrl.expertDb.label);
            $http.get(routes.expertDbStatsApi({expertDbName: normalizedDbName})).then(
                function(response) {
                    ctrl.expertDbStats = response.data;

                    if (ctrl.expertDb.label === 'lncrnadb') {  // this is lncRNAdb - display a table of RNAs
                         $http.get(routes.ebiDbSequences({ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT, dbQuery: "expert_db:lncrnadb"})).then(
                             function(response) {
                                 ctrl.lncrnadb = response.data.entries.map(item => ({
                                     id: item.id,
                                     description: item.fields.description[0],
                                     length: parseInt(item.fields.length[0])
                                 }))
                                 ctrl.lncrnadb.sort(function(a, b) { return parseInt(b.length) - parseInt(a.length); });
                             }, function(response) {
                                 ctrl.onError();
                             }
                         );
                    } else {  // this in not lncRNAdb - display a d3 diagram with length distribution
                        ExpertDatabaseSequenceDistribution("#d3-seq-length-distribution", ctrl.expertDbStats.length_counts, 500, 300, routes.textSearch());
                    }

                    // is sunburst construction is not too slow, display it
                    if (ctrl.noSunburst.indexOf(ctrl.expertDb.label) === -1) {
                        d3SpeciesSunburst(ctrl.expertDbStats.taxonomic_lineage, '#d3-species-sunburst', 500, 300);
                    }
                },
                function(response) {
                    console.log("Database stats could not be loaded");
                }
            );
        };
    }]
};

angular.module('expertDatabase').component('expertDatabaseRight', expertDatabaseRight);
