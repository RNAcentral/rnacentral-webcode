var top = {
    bindings: {
        expertDb: "<"
    },
    templateUrl: '/static/js/components/expert-database/top.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', function($interpolate, $location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // urls used in template (hardcoded)
            ctrl.routes = routes;

            /**
             * Given an expert database label (lowercase), convert it to a PK in DatabaseStats table.
             */
            ctrl.normalizeDbLabel = function(label) {
                if (label === 'tmrna-website') return "TMRNA_WEB";
                else return ctrl.expertDb.label.toUpperCase();
            };
        };
    }]
};

angular.module('expertDatabase').component('top', top);