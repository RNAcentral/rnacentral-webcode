var left = {
    bindings: {
        expertDb: "<"
    },
    templateUrl: '/static/js/components/expert-database/left.html',
    controller: ['$interpolate', '$location', '$http', 'search', 'routes', function($interpolate, $location, $http, search, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // urls used in template (hardcoded)
            ctrl.routes = routes;
        };
    }]
};

angular.module('expertDatabase').component('left', left);