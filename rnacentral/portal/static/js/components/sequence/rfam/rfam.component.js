var rfam = {
    bindings: {
        upi: '<',
        rna: '<',
        rfamHits: '<',
        toggleGoModal: '&'
    },

    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.help = "/help/rfam-annotations";

            // group hits with same rfam_model_id
            ctrl.groupedHits = [];
            ctrl.rfamHits.forEach(function(hit) {
                var existingHit = ctrl.groupedHits.find(function(existingHit) {
                    return existingHit.rfam_model_id === hit.rfam_model_id;
                });
                if (existingHit) {
                    existingHit.raw.push(hit);
                    existingHit.ranges.push([hit.sequence_start, hit.sequence_stop, hit.sequence_completeness]);
                } else {
                    ctrl.groupedHits.push({
                        raw: [hit],
                        ranges: [[hit.sequence_start, hit.sequence_stop, hit.sequence_completeness]],
                        rfam_model: hit.rfam_model,
                        rfam_model_id: hit.rfam_model.rfam_model_id
                    });
                }

            });
        };

    }],

    templateUrl: '/static/js/components/sequence/rfam/rfam.html'
};

angular.module("rnaSequence").component("rfam", rfam);
