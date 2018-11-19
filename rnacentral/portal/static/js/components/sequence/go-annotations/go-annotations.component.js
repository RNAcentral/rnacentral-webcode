var goAnnotations = {
    bindings: {
        upi: '=',
        taxid: '=',
        showGoAnnotations: '&',
        onToggleGoModal: '&'
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
            "dictybase": "http://dictybase.org/",
        };

        var annotationOrdering = function(annotation) {
            var qualifier = {
                "involved_in": 10,
                "enables": 20,
                "contributes_to": 30,
                "colocalizes_with": 40,
                "part_of": 50,
                "__unknown__": 60,
            };

            var evidence = {
                "ECO:0000314": 1,
                "ECO:0000315": 2,
                "ECO:0000353": 3,
                "ECO:0000316": 4,
                "ECO:0000270": 5,
                "__unknown__": 6,
            };

            return (qualifier[annotation.qualifier] || qualifier.__unknown__) +
                (evidence[annotation.evidence_code_id] || evidence.__unknown__);
        };

        ctrl.$onInit = function() {
            ctrl.fetchGoTerms().then(
                function(response) {
                    ctrl.go_annotations = response.data;
                    ctrl.go_annotations.sort(ctrl.compareAnnotations);

                    ctrl.go_annotations.forEach(function(annotation) {
                        var key = annotation.assigned_by.toLowerCase();
                        annotation.assigned_url = sourceUrls[key];
                        annotation.needs_explanation = annotation.evidence_code_id == 'ECO:0000307';
                        if (annotation.needs_explanation) {
                            annotation.explanation_url = 'http://wiki.geneontology.org/index.php/No_biological_Data_available_(ND)_evidence_code';
                        }
                    });

                    if (ctrl.go_annotations.length) {
                        ctrl.showGoAnnotations();
                    }
                },
                function(response) {
                    ctrl.error = "Failed to fetch GO annotations";
                }
            );
        };

        ctrl.compareAnnotations = function(first, second) {
            return annotationOrdering(first) - annotationOrdering(second);
        };

        ctrl.fetchGoTerms = function() {
            return $http.get(
                routes.apiGoTermsView({ upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 20000 }
            );
        };

        ctrl.openGoModal = function(termId) {
            ctrl.onToggleGoModal({termId: termId});
        };
    }],

    templateUrl: '/static/js/components/sequence/go-annotations/go-annotations.html'
};

angular.module("rnaSequence").component("goAnnotations", goAnnotations);
