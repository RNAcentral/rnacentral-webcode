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
            ctrl.noSunburst = ['ena', 'rfam', 'silva', 'greengenes', 'lncipedia'];  // don't show sunburst for these databases
            ctrl.expertDbStats = null;

            // retrieve databaseStats from server, render them, if success
            var normalizedDbName = normalizeExpertDbName.labelToDb(ctrl.expertDb.label);
            $http.get(routes.expertDbStatsApi({expertDbName: normalizedDbName})).then(
                function(response) {
                    ctrl.expertDbStats = response.data;

                    if (ctrl.expertDb.label === 'lncrnadb') {  // this is lncRNAdb - display a table of RNAs
                         $http.get(routes.apiRnaView({upi: ""}).slice(0, -1) + '?database=LNCRNADB&page_size=1000000000').then(
                             function(response) {
                                 ctrl.lncrnadb = response.data.results.slice(0);  // clone array with slice(0)
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
                    ctrl.onError();
                }
            );
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

angular.module('expertDatabase').component('expertDatabaseRight', expertDatabaseRight);