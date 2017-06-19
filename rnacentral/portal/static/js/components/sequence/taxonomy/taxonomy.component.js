var taxonomy = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate',  function($http, $interpolate) {
        var ctrl = this;

        ctrl.$onInit = function() {
            var d3_species_tree = $('#d3-species-tree');

            if (!document.createElement('svg').getAttributeNS) {
                d3_species_tree.html('Your browser does not support SVG');
            }
            else {
                $http.get($interpolate("/rna/{{upi}}/lineage")({ upi: ctrl.upi })).then(
                    function(response) {
                        ctrl.response = response;
                        d3SpeciesTree(response.data, ctrl.upi, '#d3-species-tree');
                    },
                    function(response) {
                        ctrl.response = response;
                    }
                )
            }
        };
    }],
    template: '<div id="d3-species-tree">' +
              '    <div ng-if="!$ctrl.response">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading taxonomic tree...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.response.status >= 400" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
              '    </div>' +
              '</div>'
};