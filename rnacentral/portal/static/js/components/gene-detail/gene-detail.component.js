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
    controller: ['$timeout', '$element', '$scope', '$http', function($timeout, $element, $scope, $http) {
        var vm = this;
        
        // State management
        vm.activeTab = 'transcripts';  // Default to transcripts tab
        vm.isLoading = false;
        vm.error = null;
        
        // Init empty data object
        vm.geneData = {
            name: '',
            symbol: '',
            chromosome: '',
            startPosition: '',
            endPosition: '',
            strand: '',
            geneType: '',
            summary: '',
            length: 0
        };

        vm.transcripts = [];
        vm.externalLinks = [];

        vm.$onInit = function() {
        
            
            // Check if gene was found - read from global data
            var globalData = window.geneDetailData || {};
        
            
            var geneFound = globalData.geneFound !== undefined ? globalData.geneFound : vm.geneFound;
            console.log('Final geneFound value:', geneFound);
            
            if (geneFound === 'false' || geneFound === false || geneFound === 'False') {
                console.log('Gene not found, setting error');
                vm.error = 'Gene "' + vm.geneName + '" not found in database';
                vm.geneData = {
                    name: vm.geneName || 'Unknown',
                    symbol: vm.geneName || 'Unknown'
                };
                return;
            }

            // Use global data if available
            if (globalData.geneData) {
                console.log('Using global gene data:', globalData.geneData);
                console.log('Type of global gene data:', typeof globalData.geneData);
                processGeneData(globalData.geneData);
                
                // Set transcripts and external links from global data
                vm.transcripts = globalData.transcriptsData || [];
                vm.externalLinks = globalData.externalLinksData || [];
                console.log('Set transcripts:', vm.transcripts);
                console.log('Set external links:', vm.externalLinks);
                
            } else {
                console.log('No global gene data available');
                console.log('Fallback - trying to use component attributes');
                console.log('vm.geneData:', vm.geneData);
                
                // Fallback to parsing from attributes (for backwards compatibility)
                if (vm.geneData) {
                    try {
                        var parsedData;
                        if (typeof vm.geneData === 'string') {
                            console.log('Parsing gene data string:', vm.geneData);
                            parsedData = JSON.parse(vm.geneData);
                        } else if (typeof vm.geneData === 'object') {
                            console.log('Gene data is already an object:', vm.geneData);
                            parsedData = vm.geneData;
                        } else {
                            throw new Error('Invalid data type: ' + typeof vm.geneData);
                        }
                        console.log('Parsed gene data:', parsedData);
                        processGeneData(parsedData);
                    } catch (e) {
                        console.error('Error parsing gene data:', e);
                        vm.error = 'Error loading gene data: ' + e.message;
                        vm.geneData = {
                            name: vm.geneName || 'Unknown',
                            symbol: vm.geneName || 'Unknown'
                        };
                    }
                } else {
                    console.warn('No gene data provided to component');
                    vm.geneData = {
                        name: vm.geneName || 'Unknown',
                        symbol: vm.geneName || 'Unknown'
                    };
                }
            }
            
            console.log('Final vm.geneData after processing:', vm.geneData);
            console.log('=== END ANGULARJS COMPONENT DEBUG ===');
                        
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
            console.log('Processing gene data:', data);
            
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
                geneType: data.geneType || 'Unknown',
                summary: data.summary || 'No summary available',
                length: data.length || 0,
                start: data.start || 0,
                stop: data.stop || 0,
                version: data.version || vm.geneVersion
            };

            // Calculate derived properties
            if (!vm.geneData.length && vm.geneData.start && vm.geneData.stop) {
                vm.geneData.length = Math.abs(vm.geneData.stop - vm.geneData.start) + 1;
            }

            console.log('Processed gene data:', vm.geneData);
            vm.error = null;
        }
        
        // Tab management
        vm.showTab = function(tabName) {
            vm.activeTab = tabName;
            
            // Update genome browser display when switching to that tab
            if (tabName === 'genome-browser') {
                $timeout(function() {
                    updateGenomeBrowserDisplay();
                }, 50);
            }
        };

        // Event handlers
        vm.onExternalLinkClick = function(link) {
            console.log('External link clicked:', link.url);
            // Track analytics if available
            if (window.ga) {
                window.ga('send', 'event', 'External Link', 'click', link.name);
            }
        };

        vm.onTranscriptClick = function(transcript) {
            console.log('Transcript clicked:', transcript.id);
            // Could expand to show more details or navigate to transcript page
            transcript.expanded = !transcript.expanded;
        };

        vm.onExonHover = function(index, isEntering) {
            // Handle exon hover events
            if (isEntering) {
                console.log('Exon hover enter:', index);
            } else {
                console.log('Exon hover leave:', index);
            }
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

            // Add hover effects and tooltips to exons
            var exons = $element.find('.exon');
            exons.each(function(index) {
                var $exon = angular.element(this);
                $exon.on('mouseenter', function() {
                    var exonNum = index + 1;
                    $exon.attr('title', 'Exon ' + exonNum);
                    $exon.addClass('exon-hover');
                }).on('mouseleave', function() {
                    $exon.removeClass('exon-hover');
                });
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
            $element.find('.exon').off();
        };
        
    }],
    templateUrl: '/static/js/components/gene-detail/gene-detail.template.html' 
};

// Register component to existing module
angular.module("geneDetail").component("geneDetail", geneDetail);