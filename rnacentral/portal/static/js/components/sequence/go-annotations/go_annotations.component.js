var go_annotations = {
    bindings: {
        upi: '=',
        taxid: '=',
    },

    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.fetchGoTerms().then(
                function(response) {
                    ctrl.go_annotations = response.data;
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

        ctrl.openGoChartModal = function(term_id) {
            var ontology = term_id.split(':')[0].toLowerCase();
            var png = routes.quickGoChart({ ontology: ontology, term_ids: term_id });
            $('#go-annotation-chart-modal .modal-body').html('<img src=' + png + '></img>');
            $('#go-annotation-chart-modal').modal();
        };
    }],

    templateUrl: '/static/js/components/sequence/go-annotations/go_annotations.html'
};

angular.module("rnaSequence").component("goAnnotations", go_annotations);
