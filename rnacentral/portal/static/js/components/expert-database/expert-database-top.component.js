var expertDatabaseTop = {
    bindings: {
        expertDb: "<"
    },
    templateUrl: '/static/js/components/expert-database/expert-database-top.html',
    controller: ['routes', 'normalizeExpertDbName', function(routes, normalizeExpertDbName) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // urls used in template (hardcoded)
            ctrl.routes = routes;
            ctrl.normalizeExpertDbName = normalizeExpertDbName;
        };
    }]
};

angular.module('expertDatabase').component('expertDatabaseTop', expertDatabaseTop);