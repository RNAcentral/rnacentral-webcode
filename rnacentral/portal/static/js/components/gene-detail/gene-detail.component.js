// FIXED VERSION
var geneDetail = {
    bindings: {
        geneName: '@?',
        geneVersion: '@?',
        geneData: '@?',
        transcriptsData: '@?',
        externalLinksData: '@?',
        geneFound: '@?'
    },
    controllerAs: 'vm',
    controller: ['$timeout', '$element', '$scope', '$http', '$sce', function($timeout, $element, $scope, $http, $sce) {
        var vm = this;
        
        // State management
        vm.activeTab = 'transcripts';  // Default to transcripts tab
        vm.isLoading = false;
        vm.error = null;
        vm.genomeBrowserLoaded = false;
        
        // Pagination state
        vm.transcriptsLoading = false;
        vm.pagination = {
            current_page: 1,
            total_pages: 1,
            total_count: 0,
            page_size: 10,
            has_previous: false,
            has_next: false,
            start_index: 0,
            end_index: 0
        };
        
        // Init empty data object
        vm.geneData = {
            name: '',
            symbol: '',
            chromosome: '',
            startPosition: '',
            endPosition: '',
            strand: '',
            strandDirection:'',
            geneType: '',
            shortDescription:'',
            summary: '',
            length: 0,
            species:'',
        };

        vm.transcripts = [];
        vm.externalLinks = [];
        vm.litsummSummaries = [];

        vm.$onInit = function() {
            
            // Check if gene was found - read from global data
            var globalData = window.geneDetailData || {};
        
            var geneFound = globalData.geneFound !== undefined ? globalData.geneFound : vm.geneFound;
            
            if (geneFound === 'false' || geneFound === false || geneFound === 'False') {
                vm.error = 'Gene "' + vm.geneName + '" not found in database';
                vm.geneData = {
                    name: vm.geneName || 'Unknown',
                    symbol: vm.geneName || 'Unknown'
                };
                return;
            }

            // Use global data if available
            if (globalData.geneData) {
                processGeneData(globalData.geneData);
                
                // Set transcripts, external links, and litsumm summaries from global data
                vm.transcripts = globalData.transcriptsData || [];
                vm.externalLinks = globalData.externalLinksData || [];

                // Process litsumm summaries and trust HTML content
                var rawSummaries = globalData.litsummSummaries || [];
                vm.litsummSummaries = rawSummaries.map(function(item) {
                    return {
                        id: item.id,
                        urs: item.urs,
                        summary: $sce.trustAsHtml(item.summary),
                        description: item.description || ""
                    };
                });

                // parse urs and taxid for each transcript

                if(vm.transcripts && vm.transcripts.length > 0) {
                    vm.transcripts = vm.transcripts.map(t => {
                    const [urs, taxid] = t.id.split('_')
                    const sequence_page = `/rna/${urs}/${taxid}`
                    
                    return {
                        ...t, 
                        sequence_page
                    }

                    })

                    
                }
                
                // Set pagination data
                if (globalData.transcriptsPagination) {
                    vm.pagination = angular.extend({}, vm.pagination, globalData.transcriptsPagination);
                    // Convert string booleans to actual booleans
                    vm.pagination.has_previous = vm.pagination.has_previous === 'true' || vm.pagination.has_previous === true;
                    vm.pagination.has_next = vm.pagination.has_next === 'true' || vm.pagination.has_next === true;
                }
                
            } else {
                // Fallback to parsing from attributes (for backwards compatibility)
                if (vm.geneData) {
                    try {
                        var parsedData;
                        if (typeof vm.geneData === 'string') {
                            parsedData = JSON.parse(vm.geneData);
                        } else if (typeof vm.geneData === 'object') {
                            parsedData = vm.geneData;
                        } else {
                            throw new Error('Invalid data type: ' + typeof vm.geneData);
                        }
                        processGeneData(parsedData);
                    } catch (e) {
                        vm.error = 'Error loading gene data: ' + e.message;
                        vm.geneData = {
                            name: vm.geneName || 'Unknown',
                            symbol: vm.geneName || 'Unknown'
                        };
                    }
                } else {
                    vm.geneData = {
                        name: vm.geneName || 'Unknown',
                        symbol: vm.geneName || 'Unknown'
                    };
                }

                if(vm.transcriptsPagination) {
                    try {
                        var parsedPaginationData;
                        if (typeof vm.transcriptsPagination === 'string') {
                            parsedPaginationData = JSON.parse(vm.transcriptsPagination);
                        } else if (typeof vm.transcriptsPagination === 'object') {
                            parsedPaginationData = vm.transcriptsPagination
                        } else {
                            throw new Error("Invalid data type (for transcripts pagination): " + typeof vm.transcriptsPagination)
                        }
                        vm.pagination = parsedPaginationData
                        
                    } catch(e) {
                            vm.error = 'Error loading pagination data: ' + e.message;
                    }
                }
            }
                        
            initializeKeyboardNavigation();
        };

        vm.$postLink = function() {
            // Initialize DOM-dependent functionality
            $timeout(function() {
                initializeInteractiveFeatures();
                updateGenomeBrowserDisplay();
            }, 100);
        };
        
        function processGeneData(data) {
            
            if (!data) {
                vm.error = 'No gene data available';
                return;
            }

            // Check for errors in data
            if (data.error) {
                vm.error = data.error;
                vm.geneData.name = data.name || vm.geneName || 'Unknown';
                vm.geneData.symbol = data.symbol || data.name || 'Unknown';
                return;
            }

            vm.geneData = {
                name: data.name || vm.geneName,
                symbol: data.symbol || data.name || '',
                chromosome: data.chromosome || '',
                startPosition: data.startPosition || '',
                endPosition: data.endPosition || '',
                strand: data.strand || '',
                strandDirection: data.strandDirection || '',
                geneType: data.geneType || 'Unknown',
                shortDescription: data.shortDescription || '',
                summary: data.summary || 'No summary available',
                length: data.length || 0,
                start: data.start || 0,
                stop: data.stop || 0,
                version: data.version || vm.geneVersion,
                // Add genome browser specific fields
                species: data.species || data.organism || null,
                organism: data.organism || null
            };

            // Calculate derived properties
            if (!vm.geneData.length && vm.geneData.start && vm.geneData.stop) {
                vm.geneData.length = Math.abs(vm.geneData.stop - vm.geneData.start) + 1;
            }

            vm.error = null;
        }
        
        // Pagination methods
        vm.loadPage = function(page) {
            if (vm.transcriptsLoading || page < 1 || page > vm.pagination.total_pages) {
                return;
            }
            
            vm.transcriptsLoading = true;
            
            var url = window.location.pathname;
            var params = {
                page: page,
                page_size: vm.pagination.page_size
            };

            var queryString = Object.keys(params)
            .map(key => key + '=' + params[key])
            .join('&');

            var newUrl = url + '?' + queryString;
              // Add params to the URL and reload the page
                window.location.href = newUrl

            
            $http.get(url, { params: params }).then(function(response) {
                // Parse the response to extract the new data
                var parser = new DOMParser();
                var doc = parser.parseFromString(response.data, 'text/html');
                var scriptTag = doc.querySelector('script');
                
                if (scriptTag) {
                    // Extract the JavaScript object from the script tag
                    var scriptContent = scriptTag.textContent;
                    var dataMatch = scriptContent.match(/window\.geneDetailData\s*=\s*({.*?});/s);
                    
                    if (dataMatch) {
                        try {
                            var newData = JSON.parse(dataMatch[1]);
                            vm.transcripts = newData.transcriptsData || [];
                            vm.pagination = angular.extend({}, vm.pagination, newData.transcriptsPagination);
                            // Convert string booleans to actual booleans
                            vm.pagination.has_previous = vm.pagination.has_previous === 'true' || vm.pagination.has_previous === true;
                            vm.pagination.has_next = vm.pagination.has_next === 'true' || vm.pagination.has_next === true;
                        } catch (e) {
                            vm.error = 'Error loading page data';
                        }
                    }
                }
                
                vm.transcriptsLoading = false;
            }).catch(function(error) {
                vm.error = 'Failed to load page data';
                vm.transcriptsLoading = false;
            });
        };
        
        vm.goToPage = function(page) {
            vm.loadPage(page);
        };
        
        vm.previousPage = function() {
            if (vm.pagination.has_previous) {
                vm.loadPage(vm.pagination.current_page - 1);
            }
        };
        
        vm.nextPage = function() {
            if (vm.pagination.has_next) {
                vm.loadPage(vm.pagination.current_page + 1);
            }
        };
        
        vm.getVisiblePages = function() {
            var pages = [];
            var current = vm.pagination.current_page || 1;
            var total = vm.pagination.total_pages || 1;
            var delta = 2; // Show 2 pages on each side of current
            
            if (total <= 1) {
                return [1];
            }
            
            var start = Math.max(1, current - delta);
            var end = Math.min(total, current + delta);
            
            // Add first page and ellipsis if needed
            if (start > 1) {
                pages.push(1);
                if (start > 2) {
                    pages.push('...');
                }
            }
            
            // Add visible pages
            for (var i = start; i <= end; i++) {
                pages.push(i);
            }
            
            // Add ellipsis and last page if needed
            if (end < total) {
                if (end < total - 1) {
                    pages.push('...');
                }
                pages.push(total);
            }
            
            return pages;
        };
        
        // Genome browser script loading function
        vm.loadGenomeBrowser = function() {
            // Check if script is already loaded
            if (vm.genomeBrowserLoaded || 
                window.RNACentralGenomeBrowser || 
                document.querySelector('script[src*="genome-browser.js"]')) {
                return Promise.resolve();
            }
            
            return new Promise(function(resolve, reject) {
                
                const isLocalOrTest = window.location.hostname === 'localhost' || 
                                     window.location.hostname.includes('test.rnacentral.org');
                
                const scriptSrc = isLocalOrTest 
                    ? '/static/rnacentral-genome-browser/build/genome-browser.js'
                    : 'https://rnacentral.github.io/rnacentral-genome-browser/build/genome-browser.js';
                
                const script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = scriptSrc;
                
                script.onload = function() {
                    vm.genomeBrowserLoaded = true;
                    $scope.$apply(); // Trigger digest cycle
                    resolve();
                };
                
                script.onerror = function(error) {
                    reject(error);
                };
                
                document.head.appendChild(script);
            });
        };
        
       vm.getGenomeBrowserData = function() {
            var browserData = {};
            
            browserData.species = vm.geneData.species;

            if (vm.geneData.chromosome) {
                browserData.chromosome = vm.geneData.chromosome;
            }

            if (vm.geneData.start || vm.geneData.startPosition) {
                browserData.start = vm.geneData.start || vm.geneData.startPosition;
            }
            
            if (vm.geneData.stop || vm.geneData.endPosition) {
                browserData.end = vm.geneData.stop || vm.geneData.endPosition;
            }
            
            browserData.geneData = {
                name: vm.geneData.name,
                symbol: vm.geneData.symbol,
                chromosome: vm.geneData.chromosome,
                start: vm.geneData.start || vm.geneData.startPosition,
                end: vm.geneData.stop || vm.geneData.endPosition,
                strand: vm.geneData.strand
            };
            
            return browserData;
        };
        
        // Tab management - FIXED: Only create element once, don't remove existing ones
        vm.showTab = function(tabName) {
            vm.activeTab = tabName;
            
            // Load genome browser script when switching to that tab
            if (tabName === 'genome-browser') {
                
                // Create the element with data immediately
                $timeout(function() {
                    var container = document.querySelector('.gene__genome-browser div[style*="padding-left"]');
                    if (container) {
                        var existingElement = container.querySelector('rnacentral-genome-browser');
                        
                        // FIXED: Only create if it doesn't exist, don't remove existing ones
                        if (!existingElement) {
                            // Load script and then create element with data
                            vm.loadGenomeBrowser().then(function() {
                                
                                var genomeBrowserData = vm.getGenomeBrowserData();
                                
                                var newElement = document.createElement('rnacentral-genome-browser');
                                newElement.setAttribute('data', JSON.stringify(genomeBrowserData));
                                
                                container.appendChild(newElement);
                                
                            }).catch(function(error) {
                                // Error handled silently
                            });
                        }
                    }
                }, 50);
            }
        };

        // Event handlers
        vm.onExternalLinkClick = function(link) {
            // Track analytics if available
            if (window.ga) {
                window.ga('send', 'event', 'External Link', 'click', link.name);
            }
        };

        vm.onTranscriptClick = function(transcript) {
            // Handle transcript click events 

        };

        // Utility functions
        vm.formatValue = function(value) {
            if (value === null || value === undefined || value === '') {
                return 'N/A';
            }
            if (angular.isNumber(value)) {
                return value.toLocaleString();
            }
            return value;
        };

        vm.hasValue = function(value) {
            return value && value !== '' && value !== null && 
                   value !== undefined && value !== 'N/A';
        };

        vm.hasTranscripts = function() {
            return vm.transcripts && vm.transcripts.length > 0;
        };

        vm.hasExternalLinks = function() {
            return vm.externalLinks && vm.externalLinks.length > 0;
        };

        function updateGenomeBrowserDisplay() {
            // Update genome browser visualization based on gene data
            if (vm.geneData.start && vm.geneData.stop) {
                var geneLength = vm.geneData.stop - vm.geneData.start;
                // Additional genome browser update logic can go here
            }
        }

        function initializeInteractiveFeatures() {
            // Add hover effects to transcript items
            var transcriptItems = $element.find('.gene__transcript-item');
            transcriptItems.on('mouseenter', function() {
                angular.element(this).addClass('hovered');
            }).on('mouseleave', function() {
                angular.element(this).removeClass('hovered');
            });

            // Add hover effects to external links
            var externalLinks = $element.find('.gene__external-link');
            externalLinks.on('mouseenter', function() {
                angular.element(this).addClass('hovered');
            }).on('mouseleave', function() {
                angular.element(this).removeClass('hovered');
            });

        }

        function initializeKeyboardNavigation() {
            vm.keydownHandler = function(event) {
                if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
                    var tabs = ['transcripts', 'genome-browser'];
                    var currentIndex = tabs.indexOf(vm.activeTab);
                    var nextIndex;

                    if (event.key === 'ArrowRight') {
                        nextIndex = (currentIndex + 1) % tabs.length;
                    } else {
                        nextIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1;
                    }

                    $scope.$apply(function() {
                        vm.showTab(tabs[nextIndex]);
                    });
                }
            };

            document.addEventListener('keydown', vm.keydownHandler);
        }

        // Cleanup
        vm.$onDestroy = function() {
            if (vm.keydownHandler) {
                document.removeEventListener('keydown', vm.keydownHandler);
            }
            
            // Remove any event listeners
            $element.off();
            $element.find('.gene__transcript-item').off();
            $element.find('.gene__external-link').off();
        };
        
    }],
    templateUrl: '/static/js/components/gene-detail/gene-detail.template.html' 
};

// Register component to existing module
angular.module("geneDetail").component("geneDetail", geneDetail);