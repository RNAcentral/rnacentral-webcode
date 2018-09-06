var rfam = {
    bindings: {
        upi: '<',
        rna: '<',
        rfamHits: '<'
    },

    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.groupedHits = [];

            ctrl.rfamHitFamilies = ctrl.rfamHits
                .map(function(hit) { return hit.rfam_model})
                .sort();

            // aggregate features with same id and different locations
            ctrl.rfamHits.forEach(function(hit) {
                var hitClone = ctrl.groupedHits.find(function(el) { return el.metadata.crs_id === hit.metadata.crs_id });
                if (!hitClone) {
                    hitClone = JSON.parse(JSON.stringify(hit));
                    hitClone.locations = [{ start: hit.start, stop: hit.stop }];
                    ctrl.groupedHits.push(hitClone);
                } else {
                    hitClone.locations.push({ start: hit.start, stop: hit.stop });
                }
            });
        };

    }],

    templateUrl: '/static/js/components/sequence/rfam/rfam.html'
};

angular.module("rnaSequence").component("rfam", rfam);