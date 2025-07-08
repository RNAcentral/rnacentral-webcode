var expressionAtlas = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', 'routes', '$timeout', function($http, $interpolate, routes, $timeout) {
        var ctrl = this;
        ctrl.isLoading = true;
        ctrl.hasError = false;
        ctrl.errorMessage = '';

        ctrl.$onInit = function() {
            ctrl.fetchGeneAndSpecies().then(
                function(response) {
                    ctrl.processResponse(response);
                },
                function(error) {
                    ctrl.handleError("Failed to fetch gene and species data", error);
                }
            );
        };

        ctrl.processResponse = function(response) {
            try {
                // Process genes
                var genes = response.data.genes || [];
                var ensemblGenes = genes.filter(function(item) { 
                    return item && typeof item === 'string' && item.startsWith('ENS'); 
                });
                
                // Process gene
                if (ensemblGenes.length > 0) {
                    ctrl.gene = ensemblGenes[0].split('.')[0];
                } else {
                    ctrl.gene = null;
                }
                
                // Process species
                ctrl.species = response.data.species || null;
                
                // Small delay to ensure DOM is ready
                $timeout(function() {
                    ctrl.renderWidget();
                }, 100);
                
            } catch (error) {
                ctrl.handleError("Error processing response data", error);
            }
        };

        ctrl.renderWidget = function() {
            try {
                // Check if library is loaded
                if (typeof expressionAtlasHeatmapHighcharts === 'undefined') {
                    ctrl.handleError("Expression Atlas library not loaded", null);
                    return;
                }
                
                // Check container
                var container = document.getElementById('highchartsContainer');
                if (!container) {
                    ctrl.handleError("Target container not found", null);
                    return;
                }
                
                // Simple single configuration approach
                var config = {
                    target: 'highchartsContainer',
                    experiment: 'reference',
                    query: {
                        species: ctrl.species || 'homo sapiens',
                        gene: ctrl.gene ? [{value: ctrl.gene}] : [{value: 'ENSG00000139618'}]
                    },
                    failSilently: true,
                    minExpressionLevel: 0.1,
                    showAnatomogram: false,
                    showControls: true,
                    showTooltips: true,
                    isWidget: true,
                    height: 400,
                    onLoad: function() {
                        ctrl.isLoading = false;
                        ctrl.hasError = false;
                        $timeout(function() {
                            ctrl.isLoading = false;
                            ctrl.hasError = false;
                        });
                    },
                    onError: function(error) {
                        // Don't show error immediately, let the widget try to recover
                        $timeout(function() {
                            if (ctrl.isLoading) {
                                ctrl.handleError("Expression data not available for this RNA sequence", error);
                            }
                        }, 5000);
                    }
                };
                
                // Don't manipulate the container DOM - let Expression Atlas handle it
                // Just render the widget directly
                expressionAtlasHeatmapHighcharts.render(config);
                
            } catch (error) {
                ctrl.handleError("Error rendering widget", error);
            }
        };

        ctrl.handleError = function(message, error) {
            ctrl.isLoading = false;
            ctrl.hasError = true;
            ctrl.errorMessage = message;
            
            // Try to show error in container if it exists
            var container = document.getElementById('highchartsContainer');
            if (container) {
                container.innerHTML = '<div class="alert alert-warning">' +
                    '<i class="fa fa-exclamation-triangle"></i> ' +
                    '<strong>Expression Atlas data unavailable</strong><br>' +
                    'This may be due to limited expression data for this RNA sequence. ' +
                    'Expression Atlas requires sufficient baseline expression data to display results.' +
                    '</div>';
            }
            
            // Apply changes to Angular scope
            if (ctrl.$apply) {
                try {
                    ctrl.$apply();
                } catch (e) {
                    // $apply may fail if already in digest cycle
                }
            }
        };

        ctrl.fetchGeneAndSpecies = function() {
            return $http.get(routes.apiRnaViewWithTaxid({ upi: ctrl.upi, taxid: ctrl.taxid }), {
                timeout: 20000
            });
        };

        ctrl.retry = function() {
            ctrl.isLoading = true;
            ctrl.hasError = false;
            ctrl.errorMessage = '';
            ctrl.$onInit();
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