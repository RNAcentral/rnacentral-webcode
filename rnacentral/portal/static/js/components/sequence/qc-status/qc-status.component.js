angular.module("rnaSequence").component("qcStatus", {
    bindings: {
        qcStatus: '<',
    },
    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
	var ctrl = this;
    }],

    templateUrl: '/static/js/components/sequence/qc-status/qc-status.html'
});
