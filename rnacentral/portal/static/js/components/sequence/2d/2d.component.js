var secondary_structures = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', 'routes', function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.fornaSize = 500;

        ctrl.$onInit = function() {
            ctrl.fetchSecondaryStructures().then(
                function(response) {
                  console.log(response);
                    ctrl.secondaryStructures = response.data.data;
                    var container = new fornac.FornaContainer("#rna_ss", {
                        'applyForce': false,
                        'allowPanningAndZooming': true,
                        'initialSize':[ctrl.fornaSize, ctrl.fornaSize],
                    });
                    var options = {
                        'structure': ctrl.secondaryStructures.secondary_structures[0].secondary_structure,
                        'sequence': ctrl.secondaryStructures.sequence,
                    };
                    console.log(ctrl.secondaryStructures);
                    container.addRNA(options.structure, options);
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
    }],
    template: '<div id="2d" style="min-height: 600px">' +
              '    <h2>Secondary structure</h2>' +
              '    <div class="col-md-6">' +
              '      <p>' +
              '        Predicted using tRNAScan-SE (source: <a href="http://gtrnadb.ucsc.edu/">GtRNAdb</a>).' +
              '      </p>' +
              '      <div id="rna_ss" style="width: {{ ctrl.fornaSize }}px; height: {{ ctrl.fornaSize }}px; margin-left: 9px;"></div>' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("secondaryStructures", secondary_structures);
