var geneDetail = {
    bindings: {
        geneName: '@?',
        geneVersion: '@?',
        geneId: '@?'
    },
    controllerAs: 'vm',  // Add this line
    controller: ['$http', '$interpolate', 'routes', '$timeout', '$element', '$compile', '$scope', function($http, $interpolate, routes, $timeout, $element, $compile, $scope) {
        var vm = this;  // Use vm instead of ctrl
        
        // State management - attach to vm instead of $scope
        vm.activeTab = 'overview';
        vm.isLoading = false;
        vm.error = null;
        
        // Gene data - attach to vm
        vm.geneData = {
            name: 'BRCA1',
            symbol: 'ENSG00000012048',
            chromosome: '17q21.31',
            startPosition: '43,044,295',
            endPosition: '43,170,245',
            strand: 'Reverse (-)',
            geneType: 'Protein Coding',
            summary: 'BRCA1 (BRCA1 DNA Repair Associated) is a protein-coding gene that plays a critical role in DNA repair and genome stability. Mutations in BRCA1 are associated with increased risk of breast and ovarian cancers. The gene encodes a nuclear phosphoprotein that acts as a tumor suppressor.'
        };

        vm.stats = [
            { value: '24', label: 'Exons' },
            { value: '8', label: 'Transcripts' },
            { value: '125.9', label: 'kb Length' }
        ];

        vm.externalLinks = [
            { name: 'Ensembl', url: 'https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000012048' },
            { name: 'NCBI Gene', url: 'https://www.ncbi.nlm.nih.gov/gene/672' },
            { name: 'UniProt', url: 'https://www.uniprot.org/uniprot/P38398' },
            { name: 'HGNC', url: 'https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:1100' },
            { name: 'GeneCards', url: 'https://www.genecards.org/cgi-bin/carddisp.pl?gene=BRCA1' },
            { name: 'OMIM', url: 'https://www.omim.org/entry/113705' },
            { name: 'GTEx', url: 'https://www.gtexportal.org/home/gene/BRCA1' },
            { name: 'gnomAD', url: 'https://gnomad.broadinstitute.org/gene/ENSG00000012048' }
        ];

        vm.transcripts = [
            {
                id: 'ENST00000012048',
                type: 'Protein Coding',
                length: '7,833 bp',
                exons: 24,
                cdsLength: '5,592 bp',
                protein: 'ENSP00000350283',
                uniProt: 'P38398',
                tsl: '1 (best)'
            },
            {
                id: 'ENST00000357654',
                type: 'Protein Coding',
                length: '8,048 bp',
                exons: 22,
                cdsLength: '5,592 bp',
                protein: 'ENSP00000350283',
                uniProt: 'P38398-2',
                tsl: '1'
            },
            {
                id: 'ENST00000468300',
                type: 'Nonsense Mediated Decay',
                length: '2,344 bp',
                exons: 8,
                cdsLength: 'N/A',
                protein: 'N/A',
                uniProt: 'N/A',
                tsl: '2'
            }
        ];

        vm.evidenceCards = [
            {
                title: 'Genetic Evidence',
                score: 85,
                scoreText: '0.85',
                scoreClass: 'gene__score-high',
                description: 'Strong GWAS associations with breast and ovarian cancer risk. Multiple rare variants with high penetrance.'
            },
            {
                title: 'Literature Evidence',
                score: 92,
                scoreText: '0.92',
                scoreClass: 'gene__score-high',
                description: 'Extensive literature support across multiple cancer types. Over 15,000 publications in PubMed.'
            },
            {
                title: 'Animal Models',
                score: 68,
                scoreText: '0.68',
                scoreClass: 'gene__score-medium',
                description: 'Mouse knockout models demonstrate embryonic lethality. Heterozygous mice show increased cancer susceptibility.'
            },
            {
                title: 'Drug Evidence',
                score: 45,
                scoreText: '0.45',
                scoreClass: 'gene__score-medium',
                description: 'PARP inhibitors show efficacy in BRCA1-deficient tumors. Several clinical trials completed.'
            }
        ];

        vm.safetyCards = [
            {
                title: 'Gene Essentiality',
                scoreText: 'High Risk',
                score: 85,
                scoreClass: 'gene__score-low',
                description: 'Essential for DNA repair and genomic stability. Knockout is embryonic lethal in multiple model organisms.'
            },
            {
                title: 'Tissue Expression',
                scoreText: 'Moderate Risk',
                score: 70,
                scoreClass: 'gene__score-medium',
                description: 'Widely expressed across tissues with highest expression in breast, ovarian, and testicular tissues.'
            },
            {
                title: 'Known ADRs',
                scoreText: 'Moderate',
                score: 40,
                scoreClass: 'gene__score-medium',
                description: 'PARP inhibitor therapies targeting BRCA-deficient tumors show manageable toxicity profile.'
            }
        ];

        vm.$onInit = function() {
            // Use bindings if provided
            if (vm.geneName) {
                vm.geneData.name = vm.geneName;
            }
            if (vm.geneVersion) {
                vm.geneData.version = vm.geneVersion;
            }
            
            // Could fetch gene data here if geneId is provided
            if (vm.geneId) {
                fetchGeneData();
            }
            
            initializeKeyboardNavigation();
        };

        vm.$postLink = function() {
            // Initialize any DOM-dependent functionality
            $timeout(function() {
                initializeInteractiveFeatures();
            }, 100);
        };
        
        function fetchGeneData() {
            if (!vm.geneId) return;
            
            vm.isLoading = true;
            vm.error = null;
            
            // Example URL - adjust based on your API
            var url = '/api/genes/' + vm.geneId + '/';
            
            $http.get(url).then(
                function(response) {
                    vm.geneData = angular.extend(vm.geneData, response.data);
                    vm.isLoading = false;
                },
                function(error) {
                    vm.error = 'Failed to load gene data';
                    vm.isLoading = false;
                    console.error('Gene data fetch error:', error);
                }
            );
        }
        
        // Tab management - attach to vm
        vm.showTab = function(tabName) {
            vm.activeTab = tabName;
            
            // Animate score bars if evidence or safety tab is shown
            if (tabName === 'evidence' || tabName === 'safety') {
                $timeout(function() {
                    animateScoreBars();
                }, 300);
            }
        };

        // Event handlers - attach to vm
        vm.onExternalLinkClick = function(link) {
            console.log('External link clicked:', link.url);
            // Analytics tracking will be handled by the main app's event delegation
        };

        vm.onTranscriptClick = function(transcript) {
            console.log('Transcript clicked:', transcript.id);
            // Could expand to show more details or navigate to transcript view
        };

        vm.onExonHover = function(index, isEntering) {
            console.log('Exon ' + (index + 1) + (isEntering ? ' entered' : ' left'));
            // Could show tooltip or highlight related elements
        };

        // Utility functions - attach to vm
        vm.formatValue = function(value) {
            if (angular.isNumber(value)) {
                return value.toLocaleString();
            }
            return value;
        };

        vm.hasValue = function(value) {
            return value && value !== '' && value !== null && value !== undefined;
        };

        function animateScoreBars() {
            var scoreFills = $element.find('.gene__score-fill');
            
            scoreFills.each(function(index, fill) {
                var $fill = angular.element(fill);
                var targetWidth = $fill.css('width');
                $fill.css('width', '0%');
                
                $timeout(function() {
                    $fill.css('width', targetWidth);
                }, 100 + (index * 50)); // Stagger animations
            });
        }

        function initializeInteractiveFeatures() {
            // Add hover effects to evidence cards
            var evidenceCards = $element.find('.gene__evidence-card');
            evidenceCards.on('mouseenter', function() {
                angular.element(this).addClass('hovered');
            }).on('mouseleave', function() {
                angular.element(this).removeClass('hovered');
            });

            // Add hover effects to exons
            var exons = $element.find('.exon');
            exons.each(function(index) {
                var $exon = angular.element(this);
                $exon.on('mouseenter', function() {
                    $exon.attr('title', 'Exon ' + (index + 1));
                    $exon.addClass('exon-hover');
                    vm.onExonHover(index, true);
                }).on('mouseleave', function() {
                    $exon.removeClass('exon-hover');
                    vm.onExonHover(index, false);
                });
            });
        }

        function initializeKeyboardNavigation() {
            vm.keydownHandler = function(event) {
                if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
                    var tabs = ['overview', 'transcripts', 'genome-browser', 'safety'];
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
        };
        
    }],
    templateUrl: '/static/js/components/gene-detail/gene-detail.template.html' 
};

angular.module("geneDetail", []).component("geneDetail", geneDetail);