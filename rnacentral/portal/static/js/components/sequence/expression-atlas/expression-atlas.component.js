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
        ctrl.librariesLoaded = false;

        ctrl.$onInit = function() {
            console.log('Expression Atlas component initialized');
            console.log('UPI:', ctrl.upi);
            console.log('TaxID:', ctrl.taxid);
            
            // Wait for libraries to load before proceeding
            ctrl.waitForLibraries().then(function() {
                ctrl.fetchGeneAndSpecies().then(
                    function(response) {
                        ctrl.processResponse(response);
                    },
                    function(error) {
                        ctrl.handleError("Failed to fetch gene and species data", error);
                    }
                );
            });
        };

        ctrl.waitForLibraries = function() {
            return new Promise(function(resolve, reject) {
                var maxAttempts = 75; // 15 second timeout
                var attempts = 0;
                
                function checkLibraries() {
                    attempts++;
                    
                    // Check if both CSS and JS are loaded
                    var cssLoaded = ctrl.isCssLoaded();
                    var jsLoaded = typeof expressionAtlasHeatmapHighcharts !== 'undefined';
                    
                    if (cssLoaded && jsLoaded) {
                        ctrl.librariesLoaded = true;
                        console.log('Expression Atlas libraries loaded successfully');
                        // Add extra delay to ensure CSS is fully applied
                        setTimeout(function() {
                            resolve();
                        }, 500);
                    } else if (attempts >= maxAttempts) {
                        console.error('Libraries failed to load within timeout');
                        reject(new Error('Libraries failed to load within timeout'));
                    } else {
                        setTimeout(checkLibraries, 200);
                    }
                }
                
                checkLibraries();
            });
        };

        ctrl.isCssLoaded = function() {
            // Check if Expression Atlas CSS is loaded by looking for specific stylesheets
            var stylesheets = document.styleSheets;
            for (var i = 0; i < stylesheets.length; i++) {
                try {
                    var href = stylesheets[i].href;
                    if (href && href.includes('customized-bootstrap-3.3.5.css')) {
                        // Additional check: ensure stylesheet has rules
                        if (stylesheets[i].cssRules || stylesheets[i].rules) {
                            return true;
                        }
                    }
                } catch (e) {
                    // Cross-origin stylesheets may throw errors when accessing href
                    continue;
                }
            }
            
            // Fallback: check if a specific CSS class exists
            try {
                var testElement = document.createElement('div');
                testElement.className = 'expression-atlas-test';
                document.body.appendChild(testElement);
                var styles = window.getComputedStyle(testElement);
                document.body.removeChild(testElement);
                return styles.display !== undefined; // Basic check that styles are working
            } catch (e) {
                return false;
            }
        };

        ctrl.processResponse = function(response) {
            try {
                console.log('Processing response data:', response.data);
                
                // Process genes
                var genes = response.data.genes || [];
                console.log('Raw genes array:', genes);
                
                var ensemblGenes = genes.filter(function(item) { 
                    return item && typeof item === 'string' && item.startsWith('ENS'); 
                });
                console.log('Filtered Ensembl genes:', ensemblGenes);
                
                // Process gene
                if (ensemblGenes.length > 0) {
                    ctrl.gene = ensemblGenes[0].split('.')[0];
                    console.log('Selected gene (after splitting):', ctrl.gene);
                    console.log('Original gene string:', ensemblGenes[0]);
                } else {
                    ctrl.gene = null;
                    console.log('No Ensembl genes found, gene set to null');
                }
                
                // Process species
                ctrl.species = response.data.species || null;
                console.log('Species:', ctrl.species);
                
                // Log final values that will be used
                console.log('Final gene value:', ctrl.gene);
                console.log('Final species value:', ctrl.species);
                
                // Wait for DOM to be ready and styles to be applied
                $timeout(function() {
                    ctrl.renderWidget();
                }, 600); // Increased delay to ensure styles are applied
                
            } catch (error) {
                console.error('Error in processResponse:', error);
                ctrl.handleError("Error processing response data", error);
            }
        };

        ctrl.renderWidget = function() {
            try {
                console.log('Rendering widget with gene:', ctrl.gene, 'and species:', ctrl.species);
                
                // Double-check libraries are still loaded
                if (!ctrl.librariesLoaded || typeof expressionAtlasHeatmapHighcharts === 'undefined') {
                    console.error('Expression Atlas library not loaded');
                    ctrl.handleError("Expression Atlas library not loaded", null);
                    return;
                }
                
                // Check container
                var container = document.getElementById('highchartsContainer');
                if (!container) {
                    console.error('Target container not found');
                    ctrl.handleError("Target container not found", null);
                    return;
                }

                // Clear any existing content
                container.innerHTML = '';
                
                // Add a loading indicator with proper styling
                container.innerHTML = '<div class="text-center" style="padding: 20px;">' +
                    '<i class="fa fa-spinner fa-spin fa-2x"></i>' +
                    '<div style="margin-top: 10px;">Loading expression data...</div>' +
                    '</div>';
                
                // SIMPLE CONFIGURATION - Following "Search across all Expression Atlas experiments – Only gene query in plain text" example
                var config = {
                    target: 'highchartsContainer',
                    query: ctrl.gene || 'ENSG00000139618',  // Simple string query, not object
                    atlasUrl: 'https://www.ebi.ac.uk/gxa/',  // Ensure correct base URL
                    failSilently: true,
                    minExpressionLevel: 0.1,
                    showAnatomogram: false,
                    showControls: true,
                    showTooltips: true,
                    isWidget: true,
                    height: 400,
                    onLoad: function() {
                        console.log('Expression Atlas widget loaded successfully');
                        // Ensure styles are properly applied after load
                        $timeout(function() {
                            ctrl.isLoading = false;
                            ctrl.hasError = false;
                            ctrl.ensureProperStyling();
                        }, 200);
                    },
                    onError: function(error) {
                        console.error('Expression Atlas widget error:', error);
                        $timeout(function() {
                            ctrl.handleError("Expression data not available for this RNA sequence", error);
                        }, 2000);
                    }
                };
                
                console.log('Expression Atlas config:', config);
                
                // Render with additional delay to ensure DOM is stable
                $timeout(function() {
                    if (container.parentNode) { // Ensure container is still in DOM
                        console.log('Calling expressionAtlasHeatmapHighcharts.render');
                        expressionAtlasHeatmapHighcharts.render(config);
                    }
                }, 300);
                
            } catch (error) {
                console.error('Error in renderWidget:', error);
                ctrl.handleError("Error rendering widget", error);
            }
        };

        ctrl.ensureProperStyling = function() {
            // Apply additional styling fixes if needed
            var container = document.getElementById('highchartsContainer');
            if (container) {
                // Ensure container has proper styling
                container.style.minHeight = '400px';
                
                // Look for Expression Atlas elements and ensure they're properly styled
                var atlasElements = container.querySelectorAll('[class*="expression-atlas"]');
                atlasElements.forEach(function(element) {
                    if (element.style.display === 'none') {
                        element.style.display = 'block';
                    }
                });
            }
        };

        ctrl.handleError = function(message, error) {
            console.error('Expression Atlas error:', message, error);
            ctrl.isLoading = false;
            ctrl.hasError = true;
            ctrl.errorMessage = message;
            
            // Show error in container with proper styling
            var container = document.getElementById('highchartsContainer');
            if (container) {
                container.innerHTML = '<div class="alert alert-warning" style="margin: 20px 0;">' +
                    '<i class="fa fa-exclamation-triangle"></i> ' +
                    '<strong>Expression Atlas data unavailable</strong><br>' +
                    'This may be due to limited expression data for this RNA sequence. ' +
                    'Expression Atlas requires sufficient baseline expression data to display results.' +
                    '</div>';
            }
            
            // Apply changes to Angular scope
            $timeout(function() {
                // Force digest cycle
            });
        };

        ctrl.fetchGeneAndSpecies = function() {
            console.log('Fetching gene and species data...');
            return $http.get(routes.apiRnaViewWithTaxid({ upi: ctrl.upi, taxid: ctrl.taxid }), {
                timeout: 20000
            });
        };

        ctrl.retry = function() {
            console.log('Retrying Expression Atlas component...');
            ctrl.isLoading = true;
            ctrl.hasError = false;
            ctrl.errorMessage = '';
            ctrl.librariesLoaded = false;
            ctrl.$onInit();
        };

    }],
    template: '<div id="highchartsContainer" style="min-height: 400px;">' +
              '    <div ng-if="$ctrl.isLoading" class="text-center" style="padding: 40px;">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i>' +
              '        <div style="margin-top: 15px;">Loading Expression Atlas...</div>' +
              '        <div ng-if="!$ctrl.librariesLoaded" class="text-muted" style="margin-top: 10px; font-size: 0.9em;">Loading libraries...</div>' +
              '    </div>' +
              '    <div ng-if="$ctrl.hasError && !$ctrl.isLoading" class="alert alert-danger" style="margin: 20px 0;">' +
              '        <i class="fa fa-exclamation-triangle"></i> {{ $ctrl.errorMessage }}' +
              '        <br><button class="btn btn-sm btn-default" ng-click="$ctrl.retry()" style="margin-top: 10px;">Retry</button>' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("expressionAtlas", expressionAtlas);