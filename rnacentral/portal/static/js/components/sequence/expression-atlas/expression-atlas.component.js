var expressionAtlas = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', 'routes',  function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.fetchGeneAndSpecies().then(
                function(response) {
                    var gene = response.data.genes.filter((item) => item.startsWith('ENS'))
                    ctrl.gene = gene && gene[0] && gene[0].split('.')[0];
                    ctrl.species = response.data.species

                    expressionAtlasHeatmapHighcharts.render(
                      {
                        target: 'highchartsContainer',
                        query: {
                          species: ctrl.species,
                          gene: ctrl.gene,
                        },
                      }
                    );
                },
                function(response) {
                    ctrl.error = "Failed to fetch Expression Atlas data";
                }
            );
        };

        ctrl.fetchGeneAndSpecies = function() {
            return $http.get(routes.apiRnaViewWithTaxid({ upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 20000 }
            )
        };

    }],
    template: '<div id="highchartsContainer">' +
              '    <div ng-if="!$ctrl.response">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading Expression Atlas...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.response.status >= 400" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("expressionAtlas", expressionAtlas);
