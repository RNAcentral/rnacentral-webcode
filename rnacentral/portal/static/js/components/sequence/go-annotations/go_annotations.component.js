var go_annotations = {
    bindings: {
        upi: '=',
        taxid: '=',
    },

    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        var sourceUrls = {
            "bhf-ucl": "https://www.ucl.ac.uk/functional-gene-annotation/cardiovascular/projects",
            "sgd": "https://www.yeastgenome.org/",
            "mgi": "http://www.informatics.jax.org",
            "uniprot": "http://www.uniprot.org",
            "goc": "http://geneontology.org",
            "aruk-ucl": "http://www.ucl.ac.uk/functional-gene-annotation/neurological",
            "parkinsonsuk-ucl": "http://www.ucl.ac.uk/functional-gene-annotation/neurological",
        };

        ctrl.$onInit = function() {
            ctrl.fetchGoTerms().then(
                function(response) {
                    ctrl.go_annotations = response.data;
                    ctrl.go_annotations.forEach(function(annotation) {
                        var key = annotation.assigned_by.toLowerCase();
                        annotation.assigned_url = sourceUrls[key];
                    });
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
