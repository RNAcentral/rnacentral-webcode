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
        vm.activeTab = 'transcripts';
        vm.isLoading = false;
        vm.error = null;
        vm.genomeBrowserLoaded = false;
        
        // Gene data object
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
            length: 0
        };

        vm.transcripts = [];
        vm.externalLinks = [];

        vm.$onInit = function() {
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

            if (globalData.geneData) {
                processGeneData(globalData.geneData);
                vm.transcripts = globalData.transcriptsData || [];
                vm.externalLinks = globalData.externalLinksData || [];
            } else {
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
            }
                        
            initializeKeyboardNavigation();
        };

        vm.$postLink = function() {
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
                species: data.species || data.organism || null,
                organism: data.organism || null
            };

            if (!vm.geneData.length && vm.geneData.start && vm.geneData.stop) {
                vm.geneData.length = Math.abs(vm.geneData.stop - vm.geneData.start) + 1;
            }

            vm.error = null;
        }
        
        vm.loadGenomeBrowser = function() {
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
                    $scope.$apply();
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
            
            if (vm.geneData.species || vm.geneData.organism) {
                browserData.species = vm.geneData.species || vm.geneData.organism;
            }
            
            if (vm.geneData.chromosome) {
                browserData.chromosome = vm.geneData.chromosome;
            }
            
            if (vm.geneData.start || vm.geneData.startPosition) {
                browserData.start = vm.geneData.start || vm.geneData.startPosition;
            }
            
            if (vm.geneData.stop || vm.geneData.endPosition) {
                browserData.end = vm.geneData.stop || vm.geneData.endPosition;
            }
            
            browserData.name = vm.geneData.name;
            browserData.symbol = vm.geneData.symbol;
            browserData.strand = vm.geneData.strand;
            browserData.geneType = vm.geneData.geneType;
            browserData.summary = vm.geneData.summary;
            browserData.length = vm.geneData.length;
            
            return browserData;
        };
        
        vm.showTab = function(tabName) {
            vm.activeTab = tabName;
            
            if (tabName === 'genome-browser') {
                $timeout(function() {
                    var container = document.querySelector('.gene__genome-browser div[style*="padding-left"]');
                    if (container) {
                        var existingElement = container.querySelector('rnacentral-genome-browser');
                        
                        if (!existingElement) {
                            vm.loadGenomeBrowser().then(function() {
                                var genomeBrowserData = vm.getGenomeBrowserData();
                                var newElement = document.createElement('rnacentral-genome-browser');
                                newElement.setAttribute('data', JSON.stringify(genomeBrowserData));
                                container.appendChild(newElement);
                            }).catch(function(error) {
                                console.error('Failed to load genome browser:', error);
                            });
                        }
                    }
                }, 50);
            }
        };

        // Event handlers
        vm.onExternalLinkClick = function(link) {
            if (window.ga) {
                window.ga('send', 'event', 'External Link', 'click', link.name);
            }
        };

        vm.onTranscriptClick = function(transcript) {
            transcript.expanded = !transcript.expanded;
        };

        vm.onExonHover = function(index, isEntering) {
            // Handle exon hover events if needed
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
            if (vm.geneData.start && vm.geneData.stop) {
                var geneLength = vm.geneData.stop - vm.geneData.start;
                // Additional genome browser update logic can go here
            }
        }

        function initializeInteractiveFeatures() {
            var transcriptItems = $element.find('.gene__transcript-item');
            transcriptItems.on('mouseenter', function() {
                angular.element(this).addClass('hovered');
            }).on('mouseleave', function() {
                angular.element(this).removeClass('hovered');
            });

            var externalLinks = $element.find('.gene__external-link');
            externalLinks.on('mouseenter', function() {
                angular.element(this).addClass('hovered');
            }).on('mouseleave', function() {
                angular.element(this).removeClass('hovered');
            });

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

        vm.$onDestroy = function() {
            if (vm.keydownHandler) {
                document.removeEventListener('keydown', vm.keydownHandler);
            }
            
            $element.off();
            $element.find('.gene__transcript-item').off();
            $element.find('.gene__external-link').off();
            $element.find('.exon').off();
        };
        
    }],
    templateUrl: '/static/js/components/gene-detail/gene-detail.template.html' 
};

angular.module("geneDetail").component("geneDetail", geneDetail);