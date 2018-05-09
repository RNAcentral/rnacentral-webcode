var go_annotations = {
    bindings: {
        upi: '=',
    },

    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.fetchGoTerms().then(
                function(response) {
                    ctrl.go_terms = response.data.data;
                },
                function(response) {
                    ctrl.error = "Failed to fetch GO annotations";
                }
            );
        };

        ctrl.fetchGoTerms = function() {
            return $http.get(
                routes.apiGoTermsView({ upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 5000 }
            );
        };
    }],

    templateUrl: '/static/js/components/sequence/go_annotations/go_annotations.html'
};

angular.module("rnaSequence").component("go_annotations", go_annotations);
