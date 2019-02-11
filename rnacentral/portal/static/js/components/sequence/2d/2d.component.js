var secondary_structures = {
    bindings: {
        upi: '<',
        taxid: '<?',
        showSecondaryStructureTab: '&'
    },
    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.fornaSize = 500;
        ctrl.numStructures = 0;
        ctrl.panZoom;

        ctrl.$onInit = function() {
            ctrl.fetchSecondaryStructures().then(
                function(response) {
                    ctrl.secondaryStructures = response.data.data;
                    ctrl.secondaryStructures.useForna = !ctrl.secondaryStructures.secondary_structures[0].layout;
                    if (!ctrl.useForna) {
                        ctrl.secondaryStructures.svg = ctrl.secondaryStructures.secondary_structures[0].layout;
                    }

                    ctrl.numStructures = ctrl.secondaryStructures.secondary_structures.length;
                    ctrl.SecondaryStructureUrl = routes.apiSecondaryStructuresView({ upi: ctrl.upi, taxid: ctrl.taxid });
                    ctrl.displaySecondary();
                },
                function(response) {
                    ctrl.error = "Failed to download secondary structures";
                }
            );
        };

        ctrl.fetchSecondaryStructures = function() {
            return $http.get(routes.apiSecondaryStructuresView({ upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 5000 }
            )
        };

        ctrl.getSourceUrl = function() {
            if (ctrl.numStructures === 0) {
                return '';
            }
            return ctrl.secondaryStructures.secondary_structures[0].source[0].url;
        };

        ctrl.displaySecondary = function() {
            if (ctrl.numStructures === 0) {
                return;
            }

            if (ctrl.secondaryStructures.useForna) {
                return ctrl.displayForna();
            }
            return ctrl.displayLayout();
        };

        ctrl.displayForna = function() {
            var container = new fornac.FornaContainer("#rna_ss", {
                'applyForce': false,
                'allowPanningAndZooming': true,
                'initialSize': [ctrl.fornaSize, ctrl.fornaSize],
            });
            var options = {
                'structure': ctrl.secondaryStructures.secondary_structures[0].secondary_structure,
                'sequence': ctrl.secondaryStructures.sequence,
            };
            container.addRNA(options.structure, options);
            ctrl.showSecondaryStructureTab();
        };

        ctrl.displayLayout = function() {
            document.getElementById('rna_ss_traveler').innerHTML = ctrl.secondaryStructures.svg;
            var svg = document.querySelector('#rna_ss_traveler svg');
            if (svg) {
                svg.classList.remove('black');
                svg.classList.add('traveler-secondary-structure-svg');
                // delete inline svg styles to prevent style leakage
                var style = svg.getElementsByTagName('style');
                if (style.length > 0) {
                    var parent = style[0].parentNode;
                    parent.removeChild(style[0]);
                    var parent2 = parent.parentNode;
                    parent2.removeChild(parent);
                }
            }

            ctrl.panZoom = svgPanZoom('#rna_ss_traveler svg', {
              controlIconsEnabled: true,
              fit: false, // see https://github.com/ariutta/svg-pan-zoom/issues/100
            });

            // fix the svg control position
            $('#svg-pan-zoom-controls').attr('transform', '');
            // increase the font size
            $('.traveler-secondary-structure-svg').css('font-size', '11px');

            ctrl.showSecondaryStructureTab();
        };

        /**
         * Saves structure in dot-bracket notation as a file, code stolen from:
         * https://stackoverflow.com/questions/3665115/create-a-file-in-memory-for-user-to-download-not-through-server
         */
        ctrl.save2D = function() {
            var filename = ctrl.upi + '.dbn';
            var blob = new Blob([ctrl.secondaryStructures.secondary_structures[0].secondary_structure], {type: 'text/plain'});
            if(window.navigator.msSaveOrOpenBlob) {
                window.navigator.msSaveBlob(blob, filename);
            }
            else{
                var elem = window.document.createElement('a');
                elem.href = window.URL.createObjectURL(blob);
                elem.download = filename;
                document.body.appendChild(elem);
                elem.click();
                document.body.removeChild(elem);
            }
        };

    }],

    templateUrl: '/static/js/components/sequence/2d/2d.html'
};

angular.module("rnaSequence").component("secondaryStructures", secondary_structures);
