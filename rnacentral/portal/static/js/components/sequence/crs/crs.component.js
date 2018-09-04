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
            ctrl.features.forEach(function(feature) {
                var featureClone = ctrl.distinctFeatures.find(function(el) { return el.metadata.crs_id === feature.metadata.crs_id });
                if (!featureClone) {
                    featureClone = JSON.parse(JSON.stringify(feature));
                    featureClone.locations = [{ start: feature.start, stop: feature.stop }];
                    ctrl.distinctFeatures.push(featureClone);
                } else {
                    featureClone.locations.push({ start: feature.start, stop: feature.stop });
                }
            });

            // for each distinct feature, add links to rth page, secondary structure and alignment
            ctrl.distinctFeatures.forEach(function(feature) {
                feature.rthPageUrl = $interpolate("https://rth.dk/resources/rnannotator/crs/vert/pages/cmf.data.collection.openallmenus.php?crs={{ crs_id }}")({ crs_id: feature.metadata.crs_id });
                feature.secondaryStructureUrl = $interpolate("https://rth.dk/resources/rnannotator/crs/vert/data/figure/structure_cons/hg38_17way/M1/{{ crs_id }}_ext_liftover_17way.ss.png")({ crs_id: feature.metadata.crs_id });
                feature.alignmentUrl = $interpolate("https://rth.dk/resources/rnannotator/crs/vert/data/figure/alignment/hg38_17way/M1/{{ crs_id }}_ext_liftover_17way.aln.png")({ crs_id: feature.metadata.crs_id });
            });

        };

    }],

    templateUrl: '/static/js/components/sequence/crs/crs.html'
};

angular.module("rnaSequence").component("crs", crs);