angular.module("rnaSequence").component("qaStatus", {
    bindings: {
        qaStatus: '<',
    },
    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
	var ctrl = this;
    }],

    templateUrl: '/static/js/components/sequence/qa-status/qa-status.html'
});
