var secondary_structures = {
    bindings: {
        upi: '<',
        taxid: '<?',
        showSecondaryStructureTab: '&'
    },
    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.help = "/help/secondary-structure";

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
                { timeout: 10000 }
            )
        };

        ctrl.getSourceUrl = function() {
            if (ctrl.numStructures === 0) {
                return '';
            }
            return ctrl.secondaryStructures.secondary_structures[0].source[0].url;
        };

        ctrl.toggleColors = function() {
            var colours = ['green', 'red', 'blue'];
            colours.forEach(function(colour, index) {
                var colourOn = document.querySelectorAll('svg.traveler-secondary-structure-svg .' + colour);
                if (colourOn.length > 0) {
                    for (var i = colourOn.length - 1; i >= 0; i--) {
                        colourOn[i].classList.add('ex-' + colour);
                        colourOn[i].classList.remove(colour);
                        ctrl.secondaryStructures.svg = ctrl.secondaryStructures.svg.replace('text.' + colour, 'ex-' + colour);
                    }
                } else {
                    var colourOff = document.querySelectorAll('svg.traveler-secondary-structure-svg .ex-' + colour);
                    for (var i = colourOff.length - 1; i >= 0; i--) {
                        colourOff[i].classList.add(colour);
                        colourOff[i].classList.remove('ex-' + colour);
                        ctrl.secondaryStructures.svg = ctrl.secondaryStructures.svg.replace('ex-' + colour, 'text.' + colour);
                    }
                }
            });
        };

        ctrl.downloadPng = function() {
            document.getElementById('svg-pan-zoom-controls').setAttribute('visibility', 'hidden');
            saveSvgAsPng(document.querySelector("#rna_ss_traveler svg"), ctrl.upi + "_" + ctrl.taxid + " 2D diagram.png", {backgroundColor: 'white'}).then(function(){
                document.getElementById('svg-pan-zoom-controls').setAttribute('visibility', 'visible');
            });
        }

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

            ctrl.showSecondaryStructureTab();

            ctrl.panZoom = svgPanZoom('#rna_ss_traveler svg', {
              controlIconsEnabled: true,
              fit: false, // see https://github.com/ariutta/svg-pan-zoom/issues/100
            });

            // fix the svg control position
            $('#svg-pan-zoom-controls').attr('transform', '');
            // increase the font size
            $('.traveler-secondary-structure-svg').css('font-size', '11px');
        };

        ctrl.feedback = function() {
            document.querySelector('.doorbell-feedback').click()
        }

        ctrl.copy2D = function() {
            var rnaClipboard = new Clipboard('#copy-dot-bracket-notation', {
                "text": function () { return ctrl.secondaryStructures.secondary_structures[0].secondary_structure; }
            });
        };

        /**
         * Saves structure in SVG format as a file, code from:
         * https://stackoverflow.com/questions/3665115/create-a-file-in-memory-for-user-to-download-not-through-server
         */
        ctrl.downloadSvg = function() {
            var filename = ctrl.upi + '.svg';
            var blob = new Blob([ctrl.secondaryStructures.svg], {type: 'text/plain'});
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
