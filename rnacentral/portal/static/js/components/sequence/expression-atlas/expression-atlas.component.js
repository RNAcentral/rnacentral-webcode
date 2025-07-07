var expressionAtlas = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', '$timeout', function($http, $interpolate, $timeout) {
        var ctrl = this;
        
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
                    
                    if (!response.data || !response.data.genes) {
                        console.error('Invalid response structure:', response);
                        ctrl.error = "Invalid data structure received from API";
                        return;
                    }
                    
                    var gene = response.data.genes.filter((item) => item.startsWith('ENS'));
                    ctrl.gene = gene && gene[0] && gene[0].split('.')[0];
                    ctrl.species = response.data.species;
                    
                    console.log('Processed data:', { gene: ctrl.gene, species: ctrl.species });
                    
                    if (!ctrl.gene || !ctrl.species) {
                        console.warn('Missing required data for Expression Atlas:', { gene: ctrl.gene, species: ctrl.species });
                        ctrl.error = "Missing gene or species information for Expression Atlas";
                        return;
                    }
                    
                    // Wait for the library to load completely
                    ctrl.waitForLibraryAndRender();
                },
                function(response) {
                    console.error('API request failed:', response);
                    ctrl.loading = false;
                    ctrl.response = response;
                    ctrl.error = "Failed to fetch Expression Atlas data";
                }
            );
        };

        ctrl.waitForLibraryAndRender = function() {
            var maxAttempts = 15;
            var attempt = 0;
            
            var checkLibrary = function() {
                attempt++;
                console.log('Checking for Expression Atlas library (GitHub commit), attempt:', attempt);
                
                if (window.expressionAtlasLoadFailed) {
                    console.error('Expression Atlas library failed to load');
                    ctrl.showFallbackLink();
                    return;
                }
                
                if (typeof expressionAtlasHeatmapHighcharts !== 'undefined' && expressionAtlasHeatmapHighcharts.render) {
                    console.log('Expression Atlas library found, rendering...');
                    console.log('Library version info:', {
                        type: typeof expressionAtlasHeatmapHighcharts,
                        methods: Object.keys(expressionAtlasHeatmapHighcharts),
                        renderType: typeof expressionAtlasHeatmapHighcharts.render
                    });
                    
                    $timeout(function() {
                        ctrl.renderExpressionAtlas();
                    }, 100);
                } else if (attempt < maxAttempts) {
                    console.log('Library not ready, waiting... (attempt', attempt, 'of', maxAttempts + ')');
                    setTimeout(checkLibrary, 1000);
                } else {
                    console.error('Expression Atlas library not available after', maxAttempts, 'attempts');
                    ctrl.showFallbackLink();
                }
            };
            
            checkLibrary();
        };

        ctrl.renderExpressionAtlas = function() {
            try {
                console.log('Attempting to render Expression Atlas (GitHub commit)...');
                
                // Clear any existing content
                var container = document.getElementById('highchartsContainer');
                if (container) {
                    container.innerHTML = '<div id="expression-atlas-target"></div>';
                }
                
                // Configuration based on the specific GitHub commit
                // This commit should have the older, more stable API
                var renderConfig = {
                    target: 'expression-atlas-target',
                    atlasUrl: "https://www.ebi.ac.uk/gxa/",
                    query: {
                        species: ctrl.species,
                        gene: ctrl.gene
                    }
                };
                
                console.log('Render config for GitHub commit:', renderConfig);
                
                // Try rendering - this version should not have the seriesNames/seriesColours bug
                expressionAtlasHeatmapHighcharts.render(renderConfig);
                
                // Set a timeout to check if rendering succeeded
                setTimeout(function() {
                    var targetDiv = document.getElementById('expression-atlas-target');
                    if (targetDiv) {
                        if (targetDiv.children.length === 0) {
                            console.warn('No content rendered, trying alternative approaches...');
                            ctrl.tryAlternativeConfigs();
                        } else {
                            console.log('Expression Atlas rendered successfully!');
                        }
                    }
                }, 4000);
                
            } catch (e) {
                console.error('Error rendering Expression Atlas (GitHub commit):', e);
                console.error('Full error details:', e.stack);
                
                // Check if it's the same error we were trying to fix
                if (e.message && e.message.includes('seriesNames') && e.message.includes('seriesColours')) {
                    console.error('Still getting the seriesNames/seriesColours error - this commit may not fix it');
                }
                
                ctrl.tryAlternativeConfigs();
            }
        };

        ctrl.tryAlternativeConfigs = function() {
            try {
                console.log('Trying alternative configurations...');
                
                // Try different configuration formats that might work with this commit
                var configs = [
                    // Minimal config
                    {
                        target: 'expression-atlas-target',
                        species: ctrl.species,
                        gene: ctrl.gene
                    },
                    // Alternative format with geneQuery
                    {
                        target: 'expression-atlas-target',
                        geneQuery: ctrl.gene,
                        species: ctrl.species
                    },
                    // Format with explicit parameters
                    {
                        target: 'expression-atlas-target',
                        atlasUrl: "https://www.ebi.ac.uk/gxa/",
                        geneQuery: [{
                            value: ctrl.gene,
                            category: "gene"
                        }],
                        conditionQuery: [],
                        species: ctrl.species
                    },
                    // Try with different species format
                    {
                        target: 'expression-atlas-target',
                        query: {
                            species: ctrl.species.toLowerCase().replace(' ', '_'),
                            gene: ctrl.gene
                        }
                    }
                ];
                
                var tryConfig = function(configIndex) {
                    if (configIndex >= configs.length) {
                        console.error('All alternative configurations failed');
                        ctrl.showFallbackLink();
                        return;
                    }
                    
                    var config = configs[configIndex];
                    console.log('Trying config', configIndex + 1, ':', config);
                    
                    try {
                        expressionAtlasHeatmapHighcharts.render(config);
                        
                        // Check if this config worked
                        setTimeout(function() {
                            var targetDiv = document.getElementById('expression-atlas-target');
                            if (targetDiv && targetDiv.children.length > 0) {
                                console.log('Config', configIndex + 1, 'worked!');
                            } else {
                                console.log('Config', configIndex + 1, 'failed, trying next...');
                                tryConfig(configIndex + 1);
                            }
                        }, 2000);
                        
                    } catch (e) {
                        console.error('Config', configIndex + 1, 'threw error:', e.message);
                        tryConfig(configIndex + 1);
                    }
                };
                
                tryConfig(0);
                
            } catch (e) {
                console.error('Error in alternative configs:', e);
                ctrl.showFallbackLink();
            }
        };

        ctrl.showFallbackLink = function() {
            var atlasUrl = 'https://www.ebi.ac.uk/gxa/genes/' + encodeURIComponent(ctrl.gene) + 
                          '?bs=%7B%22homo%20sapiens%22%3A%5B%22ORGANISM_PART%22%5D%7D&ds=%7B%22homo%20sapiens%22%3A%5B%22ORGANISM_PART%22%5D%7D';
            
            var container = document.getElementById('highchartsContainer');
            if (container) {
                container.innerHTML = 
                    '<div class="alert alert-info">' +
                    '<h4><i class="fa fa-bar-chart"></i> Expression Atlas</h4>' +
                    '<p>Expression data for <strong>' + ctrl.gene + '</strong> in <em>' + ctrl.species + '</em> is available.</p>' +
                    '<p>' +
                    '<a href="' + atlasUrl + '" target="_blank" class="btn btn-primary">' +
                    '<i class="fa fa-external-link"></i> View Expression Heatmap' +
                    '</a>' +
                    '</p>' +
                    '<p class="text-muted small">' +
                    '<i class="fa fa-info-circle"></i> ' +
                    'Click above to view the interactive expression heatmap in Expression Atlas.' +
                    '</p>' +
                    '</div>';
            }
        };

        ctrl.fetchGeneAndSpecies = function() {
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
    template: '<div id="highchartsContainer">' +
              '    <div ng-if="$ctrl.loading">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading Expression Atlas...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.error" class="alert alert-danger">' +
              '        <i class="fa fa-exclamation-triangle"></i> {{ $ctrl.error }}' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("expressionAtlas", expressionAtlas);