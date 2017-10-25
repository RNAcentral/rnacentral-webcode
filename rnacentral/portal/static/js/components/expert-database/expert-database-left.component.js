var expertDatabaseLeft = {
    bindings: {
        expertDb: "<"
    },
    templateUrl: '/static/js/components/expert-database/expert-database-left.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', function($interpolate, $location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // expose services to the template
            ctrl.routes = routes;
            ctrl.search = search;
        };
    }]
};

angular.module('expertDatabase').component('expertDatabaseLeft', expertDatabaseLeft);