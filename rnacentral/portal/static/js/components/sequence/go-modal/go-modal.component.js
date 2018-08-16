var goModal = {
    bindings: {
        upi: '=',
        taxid: '=',
        termId: '<'
    },

    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        ctrl.openGoChartModal = function(term_id) {
            var ontology = termId.split(':')[0].toLowerCase();
            var png = routes.quickGoChart({ ontology: ontology, term_ids: termId });
            ctrl.modal_status = 'loading';
            $('#go-annotation-chart-modal').modal();

            $http.get(png, { timeout: 5000 }).then(
                function(response) {
                    ctrl.modalStatus = 'loaded';
                    ctrl.chartData = 'data:image/png;charset=utf-8;base64,' + response.data;
                },
                function(error) {
                    ctrl.modalStatus = 'failed';
                }
            );
        };
    }],

    templateUrl: '/static/js/components/sequence/go-modal/go-modal.html'
};

angular.module("rnaSequence").component("goModal", goModal);
