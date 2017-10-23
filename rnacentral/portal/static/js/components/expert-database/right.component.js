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
            var normalizedDbName = ctrl.normalizeDbLabel(ctrl.expertDb.label);
            $http.get(routes.expertDbStatsApi({expertDbName: normalizedDbName})).then(
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
                    } else {  // this is lncRNAdb - retrieve the list of RNAs from server
                         $http.get(routes.apiRnaView({upi: ""}).slice(0, -1) + '?database=LNCRNADB').then(
                             function(response) {
                                 ctrl.lncrnadb = response.data.results.sort(
                                     function(a, b) { return a.length < b.length; }
                                 );
                             }, function(response) {
                                 ctrl.onError();
                             }
                         )
                    }

                    if (ctrl.noSunburst.indexOf(ctrl.expertDb.label) === -1) {
                        d3SpeciesSunburst(ctrl.expertDbStats.taxonomic_lineage, '#d3-species-sunburst', 500, 300);
                    }
                },
                function(response) {
                    ctrl.onError();
                }
            );
        };

        /**
         * Given an expert database label (lowercase), convert it to a PK in DatabaseStats table.
         */
        ctrl.normalizeDbLabel = function(label) {
            if (label === 'tmrna-website') return "TMRNA_WEB";
            else return ctrl.expertDb.label.toUpperCase();
        };

        /**
         * Given unique rna page url, extracts urs from it.
         */
        ctrl.url2urs = function(url) {
            // if url ends with a slash, strip it
            if (url.slice(-1) === '/') url = url.slice(-1);

            // url might have a taxid, so let's just take the url fragment after 'rna'
            var breadcrumbs = url.split('/');
            for (var urlFragment = 0; urlFragment < breadcrumbs.length; urlFragment++) {
                if (breadcrumbs[urlFragment] === 'rna') return breadcrumbs[urlFragment + 1];
            }
        };
    }]
};

angular.module('expertDatabase').component('right', right);