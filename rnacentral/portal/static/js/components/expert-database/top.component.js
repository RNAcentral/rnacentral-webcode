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

            // TODO: route to expert-db-logos!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            // expert-db-logos {% static 'img/expert-db-logos/' %}{{expert_db.label}}.png
        };
    }]
};

angular.module('expertDatabase').component('top', top);