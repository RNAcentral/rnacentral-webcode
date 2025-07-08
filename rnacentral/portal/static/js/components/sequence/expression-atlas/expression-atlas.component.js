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
            console.log('Expression Atlas component initializing...');
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
                console.log('Processing response:', response);
                
                // Process genes
                var genes = response.data.genes || [];
                var ensemblGenes = genes.filter(function(item) { 
                    return item && typeof item === 'string' && item.startsWith('ENS'); 
                });
                
                console.log('Filtered genes:', ensemblGenes);
                
                // Process gene
                if (ensemblGenes.length > 0) {
                    ctrl.gene = ensemblGenes[0].split('.')[0];
                } else {
                    ctrl.gene = null;
                }
                
                // Process species
                ctrl.species = response.data.species || null;
                
                console.log('Final processed data:', {
                    gene: ctrl.gene,
                    species: ctrl.species
                });
                
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
                console.log('Attempting to render Expression Atlas widget...');
                
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
                
                // Prepare configuration with fallbacks
                var config = {
                    target: 'highchartsContainer',
                    experiment: 'reference',
                    query: {
                        species: ctrl.species || 'homo sapiens',
                        gene: ctrl.gene ? [{value: ctrl.gene}] : [{value: 'ENSG00000139618'}] // Default to a known gene
                    },
                    // Add additional configuration to handle errors
                    failSilently: true,
                    minExpressionLevel: 0.1, // Lower threshold for better results
                    onLoad: function() {
                        console.log('Expression Atlas widget loaded successfully');
                        ctrl.isLoading = false;
                        ctrl.hasError = false;
                        // Use $timeout to ensure we're in the Angular digest cycle
                        $timeout(function() {
                            ctrl.isLoading = false;
                            ctrl.hasError = false;
                        });
                    },
                    onError: function(error) {
                        console.error('Expression Atlas widget error:', error);
                        ctrl.handleError("Widget rendering failed", error);
                    }
                };
                
                console.log('Rendering with config:', config);
                
                // Clear any existing content
                container.innerHTML = '<div class="text-center"><i class="fa fa-spinner fa-spin"></i> Loading Expression Atlas data...</div>';
                
                // Render the widget
                expressionAtlasHeatmapHighcharts.render(config);
                
            } catch (error) {
                ctrl.handleError("Error rendering widget", error);
            }
        };

        ctrl.handleError = function(message, error) {
            console.error(message, error);
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
              '    <div ng-if="$ctrl.isLoading && !$ctrl.hasError" class="text-center" style="padding: 20px;">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i>' +
              '        <div style="margin-top: 10px;">Loading Expression Atlas data...</div>' +
              '    </div>' +
              '    <div ng-if="$ctrl.hasError" class="alert alert-warning">' +
              '        <i class="fa fa-exclamation-triangle"></i> ' +
              '        <strong>Expression Atlas data unavailable</strong><br>' +
              '        {{ $ctrl.errorMessage }}' +
              '        <div style="margin-top: 10px;">' +
              '            <button class="btn btn-sm btn-default" ng-click="$ctrl.retry()">' +
              '                <i class="fa fa-refresh"></i> Retry' +
              '            </button>' +
              '        </div>' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("expressionAtlas", expressionAtlas);