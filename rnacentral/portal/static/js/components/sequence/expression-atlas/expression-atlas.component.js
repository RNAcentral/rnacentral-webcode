var expressionAtlas = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;
        
        // Initialize loading state
        ctrl.loading = true;
        ctrl.error = null;
        ctrl.response = null;

        ctrl.$onInit = function() {
            console.log('Expression Atlas component initializing with:', { upi: ctrl.upi, taxid: ctrl.taxid });
            
            ctrl.fetchGeneAndSpecies().then(
                function(response) {
                    console.log('API response received:', response);
                    ctrl.response = response;
                    ctrl.loading = false;
                    
                    // Check if we have the expected data structure
                    if (!response.data || !response.data.genes) {
                        console.error('Invalid response structure:', response);
                        ctrl.error = "Invalid data structure received from API";
                        return;
                    }
                    
                    var gene = response.data.genes.filter((item) => item.startsWith('ENS'));
                    ctrl.gene = gene && gene[0] && gene[0].split('.')[0];
                    ctrl.species = response.data.species;
                    
                    console.log('Processed data:', { gene: ctrl.gene, species: ctrl.species });
                    
                    // Check if we have required data for Expression Atlas
                    if (!ctrl.gene || !ctrl.species) {
                        console.warn('Missing required data for Expression Atlas:', { gene: ctrl.gene, species: ctrl.species });
                        ctrl.error = "Missing gene or species information for Expression Atlas";
                        return;
                    }
                    
                    // Check if Expression Atlas function is available
                    if (typeof expressionAtlasHeatmapHighcharts === 'undefined') {
                        console.error('Expression Atlas library not loaded');
                        ctrl.error = "Expression Atlas library not available";
                        return;
                    }

                    try {
                        expressionAtlasHeatmapHighcharts.render({
                            target: 'highchartsContainer',
                            query: {
                                species: ctrl.species,
                                gene: ctrl.gene,
                            },
                        });
                    } catch (e) {
                        console.error('Error rendering Expression Atlas:', e);
                        ctrl.error = "Failed to render Expression Atlas visualization";
                    }
                },
                function(response) {
                    console.error('API request failed:', response);
                    ctrl.loading = false;
                    ctrl.response = response;
                    ctrl.error = "Failed to fetch Expression Atlas data";
                }
            );
        };

        ctrl.fetchGeneAndSpecies = function() {
            // Build the URL manually since routes service is not available
            var baseUrl = '/api/v1/rna/' + ctrl.upi;
            if (ctrl.taxid) {
                baseUrl += '/' + ctrl.taxid;
            }
            
            console.log('Fetching data from:', baseUrl);
            
            return $http.get(baseUrl, { timeout: 20000 })
                .catch(function(error) {
                    console.error('HTTP request error:', error);
                    throw error;
                });
        };

    }],
    template: '<div id="highchartsContainer" class="debug_this">' +
              '    <div ng-if="$ctrl.loading">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading Expression Atlas...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.error" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i> {{ $ctrl.error }}' +
              '    </div>' +
              '    <div ng-if="$ctrl.response && $ctrl.response.status >= 400" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("expressionAtlas", expressionAtlas);