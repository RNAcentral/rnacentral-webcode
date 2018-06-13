var expertDatabaseTop = {
    bindings: {
        expertDb: "<"
    },
    templateUrl: '/static/js/components/expert-database/expert-database-top.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', 'normalizeExpertDbName', function($interpolate, $location, $http, search, routes, normalizeExpertDbName) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // urls used in template (hardcoded)
            ctrl.routes = routes;
            ctrl.normalizeExpertDbName = normalizeExpertDbName;
        };
    }]
};

angular.module('expertDatabase').component('expertDatabaseTop', expertDatabaseTop);