var goModal = {
    bindings: {
        upi: '=',
        taxid: '=',
        termId: '<',
        onToggleGoModal: '<'
    },

    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.chartData = '';
        };

        ctrl.$onChanges = function(changes) {
            if (changes.termId.currentValue != null) {
                var ontology = changes.termId.currentValue.split(':')[0].toLowerCase();
                var png = routes.quickGoChart({ ontology: ontology, term_ids: changes.termId.currentValue });
                ctrl.modalStatus = 'loading';
                $('#go-annotation-chart-modal').modal();

                $http.get(png, { timeout: 10000 }).then(
                    function(response) {
                        ctrl.modalStatus = 'loaded';
                        ctrl.chartData = 'data:image/png;charset=utf-8;base64,' + response.data;
                    },
                    function(error) {
                        ctrl.modalStatus = 'failed';
                    }
                );
            }
        };

        ctrl.closeModal = function() {
            ctrl.onToggleGoModal({termId : null});
            $('#go-annotation-chart-modal').modal('toggle');
        };
    }],

    templateUrl: '/static/js/components/sequence/go-modal/go-modal.html'
};

angular.module("rnaSequence").component("goModal", goModal);
