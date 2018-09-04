var crs = {
    bindings: {
        upi: '<',
        taxid: '<',
        rna: '<',
        features: '<'
    },

    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.distinctFeatures = [];

            // aggregate features with same id and different locations

            // for each distinct feature, add links to rth page, secondary structure and alignment
            ctrl.distinctFeatures.forEach(function(feature) {
                feature.rthPageUrl = "";
                feature.secondaryStructureUrl = "";
                feature.alignmentUrl = "";
            });


        };

    }],

    templateUrl: '/static/js/components/sequence/crs/crs.html'
};

angular.module("rnaSequence").component("crs", crs);