var secondary_structures = {
    bindings: {
        upi: '<',
        taxid: '<?',
        showSecondaryStructureTab: '&'
    },
    controller: ['$http', '$interpolate', 'routes', '$interval', function($http, $interpolate, routes, $interval) {
        var ctrl = this;

        ctrl.help = "/help/secondary-structure";

        ctrl.numStructures = 0;
        ctrl.panZoom;

        ctrl.$onInit = function() {
            ctrl.fetchSecondaryStructures().then(
                function(response) {
                    ctrl.secondaryStructures = response.data.data;
                    ctrl.secondaryStructures.svg = ctrl.secondaryStructures.layout;
                    ctrl.numStructures = 1;
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
            return ctrl.secondaryStructures.source[0].url;
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
            return ctrl.displayLayout();
        };

        ctrl.resize2D = function() {
            var maxWidth = document.querySelector('#secondary_structure').clientWidth;
            document.querySelector('#rna_ss_traveler svg').setAttribute('width', maxWidth);

            var height = document.querySelector('#rna_ss_traveler svg').getAttribute('height');
            document.querySelector('#rna_ss_traveler svg').setAttribute('height', Math.max(height, 500));

            ctrl.panZoom = svgPanZoom('#rna_ss_traveler svg', {
              controlIconsEnabled: true,
              contain: true,
            });

            // fix the svg control position
            $('#svg-pan-zoom-controls').attr('transform', '');
        }

        ctrl.displayLayout = function() {
            ctrl.secondaryStructures.svg = ctrl.secondaryStructures.svg.replace('bold', 'normal').replace('4px', '3px').replace('Helvetica', 'Arial');
            document.getElementById('rna_ss_traveler').innerHTML = ctrl.secondaryStructures.svg;
            hideNumberingLinesAndLabels();
            // wait until the SVG is drawn and ready
            stop = $interval(function() {
              var maxWidth = document.querySelector('#secondary_structure').clientWidth;
              if (maxWidth !== 0) {
                $interval.cancel(stop);
                var svg = document.querySelector('#rna_ss_traveler svg');
                svg.classList.remove('black');
                svg.classList.add('traveler-secondary-structure-svg');
                document.getElementById('rna_ss_traveler').classList.add('thumbnail');
                // delete inline svg styles to prevent style leakage
                var style = svg.getElementsByTagName('style');
                if (style.length > 0) {
                    var parent = style[0].parentNode;
                    parent.removeChild(style[0]);
                    var parent2 = parent.parentNode;
                    parent2.removeChild(parent);
                }
                ctrl.resize2D();
                ctrl.showSecondaryStructureTab();
              }
            }, 100);
        };

        ctrl.feedback = function() {
            document.querySelector('.doorbell-feedback').click();
        }

        ctrl.copy2D = function() {
            var rnaClipboard = new Clipboard('#copy-dot-bracket-notation', {
                "text": function () { return ctrl.secondaryStructures.secondary_structure; }
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

        hideNumberingLinesAndLabels = function() {
            if (ctrl.secondaryStructures.source !== 'gtrnadb') {
                return;
            }
            var labels = document.querySelectorAll('#rna_ss_traveler svg .numbering-label');
            for (var i = labels.length - 1; i >= 0; i--) {
                labels[i].style.display = 'none';
            }
            var lines = document.querySelectorAll('#rna_ss_traveler svg .numbering-line');
            for (var i = lines.length - 1; i >= 0; i--) {
                lines[i].style.display = 'none';
            }
        };

    }],

    templateUrl: '/static/js/components/sequence/2d/2d.html'
};

angular.module("rnaSequence").component("secondaryStructures", secondary_structures);
