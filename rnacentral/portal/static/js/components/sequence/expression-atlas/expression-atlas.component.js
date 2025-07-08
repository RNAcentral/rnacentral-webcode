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
                    try {
                        // Filter genes that start with 'ENS'
                        console.log('Filtering genes from response data...');
                        console.log('Raw genes data:', response.data.genes);
                        
                        var gene = response.data.genes.filter((item) => item.startsWith('ENS'));
                        console.log('Filtered genes (starting with ENS):', gene);
                        
                    } catch (error) {
                        console.error('Error filtering genes:', error);
                        console.error('Response data structure:', response?.data);
                        var gene = []; // Fallback to empty array
                    }

                    try {
                        // Extract and process the first gene
                        console.log('Processing first gene...');
                        console.log('Gene array:', gene);
                        
                        ctrl.gene = gene && gene[0] && gene[0].split('.')[0];
                        console.log('Processed gene ID:', ctrl.gene);
                        
                    } catch (error) {
                        console.error('Error processing gene:', error);
                        console.error('Gene value:', gene);
                        ctrl.gene = null; // Fallback value
                    }

                    try {
                        // Set species from response
                        console.log('Setting species from response...');
                        console.log('Species data:', response.data.species);
                        
                        ctrl.species = response.data.species;
                        console.log('Set species:', ctrl.species);
                        
                    } catch (error) {
                        console.error('Error setting species:', error);
                        console.error('Response data structure:', response?.data);
                        ctrl.species = null; // Fallback value
                    }

                    // Final status log
                    console.log('Final results:');
                    console.log('ctrl.gene:', ctrl.gene);
                    console.log('ctrl.species:', ctrl.species);

                    // Render Expression Atlas widget with better error handling
                    ctrl.renderExpressionAtlas();
                },
                function(response) {
                    ctrl.error = "Failed to fetch Expression Atlas data";
                    console.error('API request failed:', response);
                }
            );
        };

        ctrl.renderExpressionAtlas = function() {
            try {
                console.log('Attempting to render Expression Atlas widget...');
                
                // Check if expressionAtlasHeatmapHighcharts is available
                if (typeof expressionAtlasHeatmapHighcharts === 'undefined') {
                    console.error('expressionAtlasHeatmapHighcharts is not loaded');
                    ctrl.error = "Expression Atlas library not loaded";
                    return;
                }

                // Check if target container exists
                var container = document.getElementById('highchartsContainer');
                if (!container) {
                    console.error('Target container #highchartsContainer not found');
                    ctrl.error = "Container element not found";
                    return;
                }

                // Use dynamic gene and species if available, otherwise fallback
                var renderConfig = {
                    target: 'highchartsContainer',
                    experiment: 'reference',
                    query: {
                        species: ctrl.species || 'mus musculus',
                        gene: ctrl.gene ? [{value: ctrl.gene}] : [{value: 'ASPM'}]
                    },
                    // Add error handling callbacks
                    onRenderSuccess: function() {
                        console.log('Expression Atlas widget rendered successfully');
                        ctrl.renderSuccess = true;
                    },
                    onRenderFailure: function(error) {
                        console.error('Expression Atlas widget render failed:', error);
                        ctrl.error = "Failed to render Expression Atlas widget";
                    }
                };

                console.log('Rendering with config:', renderConfig);
                expressionAtlasHeatmapHighcharts.render(renderConfig);

            } catch (error) {
                console.error('Error rendering Expression Atlas widget:', error);
                ctrl.error = "Error rendering Expression Atlas widget: " + error.message;
            }
        };

        ctrl.fetchGeneAndSpecies = function() {
            return $http.get(routes.apiRnaViewWithTaxid({ upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 20000 }
            )
        };

    }],
    template: '<div id="highchartsContainer">' +
              '    <div ng-if="!$ctrl.renderSuccess && !$ctrl.error">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading Expression Atlas...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.error" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>{{ $ctrl.error }}' +
              '    </div>' +
              '</div>'
};