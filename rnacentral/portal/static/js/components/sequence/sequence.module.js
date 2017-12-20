var rnaSequenceController = function($scope, $location, $window, $rootScope, $compile, $http, $q, $filter, routes, GenoverseUtils) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3];  // TODO: this might not exist!
    $scope.hide2dTab = true;
    $scope.fetchRnaError = false; // hide content and display error, if we fail to download rna from server

    // programmatically switch tabs
    $scope.activeTab = 0;
    $scope.activateTab = function(index) {
        $scope.activeTab = parseInt(index);  // have to convert index to string
    };

    // Downloads tab shouldn't be clickable
    $scope.checkTab = function($event, $selectedIndex) {
        if ($selectedIndex == 4) {
            // don't call $event.stopPropagation() - we need the link on the tab to open a dropdown;
            $event.preventDefault();
        }
    };

    // This is terribly annoying quirk of ui-bootstrap that costed me a whole day of debugging.
    // When it transcludes uib-tab-heading, it creates the following link:
    //
    // <a href ng-click="select($event)" class="nav-link ng-binding" uib-tab-heading-transclude>.
    //
    // Unfortunately, htmlAnchorDirective.compile attaches an event handler to links with empty
    // href attribute: if (!element.attr(href)) {event.preventDefault();}, which intercepts
    // the default action of our download links in Download tab.
    //
    // Thus we have to manually open files for download by ng-click.
    $scope.download = function(format) {
        $window.open('/api/v1/rna/' + $scope.upi + '.' + format, '_blank');
    };

    // function passed to the 2D component in order to show the 2D tab
    // if there are any 2D structures
    $scope.show2dTab = function() {
        $scope.hide2dTab = false;
    };

    // hopscotch guided tour
    $scope.activateTour = function () {
        // hopscotch_tour = new guidedTour;
        // hopscotch_tour.initialize();
        hopscotch.startTour($rootScope.tour, 4);  // start from step 4
    };

    $scope.fetchRna = function() {
        return $q(function(resolve, reject) {
            $http.get(routes.apiRnaView({upi: $scope.upi})).then(
                function(response) {
                    $scope.rna = response.data;
                    resolve();
                },
                function () {
                    $scope.fetchRnaError = true;
                    reject();
                }
            );
        });
    };

    // Modified nucleotides visualisation.
    $scope.activateModifiedNucleotides = function(modifications) {
        // sort modifications by position
        modifications.sort(function(a, b) {return a.position - b.position});

        // loop over modifications and insert span tags with modified nucleotide data
        var data = [];
        for (var i = 0; i < modifications.length; i++) {

            // create links to pdb and modomics, if possible
            var pdbLink = "", modomicsLink = "";
            if (modifications[i].chem_comp.pdb_url) {
                pdbLink = '<a href=\'' + modifications[i].chem_comp.pdb_url + '\' target=\'_blank\'>PDBe</a> <br>';  // note <br> in the end
            }
            if (modifications[i].chem_comp.modomics_url) {
                modomicsLink = '<a href=\'' + modifications[i].chem_comp.modomics_url + '\' target=\'_blank\'>Modomics</a>';
            }

            data.push({x: modifications[i].position, y: modifications[i].position, description: 'Modified nucleotide ' + modifications[i].chem_comp.id + modifications[i].chem_comp.one_letter_code + ' <br> ' + modifications[i].chem_comp.description });

        }

        $scope.featureViewer.addFeature({
            data: data,
            name: "Modifications",
            className: "modification",
            color: "#005572",
            type: "rect",
            filter: "type1"
        });

        // scroll to sequence <pre>, bring sequence in the viewport
        $('html, body').animate(
            { scrollTop: $('#feature-viewer').offset().top - 100 },
            1200
        );
    };

    // populate data for angular-genoverse instance
    $scope.activateGenomeBrowser = function(start, end, chr, genome) {
        $scope.Genoverse = Genoverse;
        $scope.genoverseUtils = new GenoverseUtils($scope);
        $scope.exampleLocations = $scope.genoverseUtils.exampleLocations;

        // add some padding to both sides of feature
        var length = end - start;
        $scope.start = start - Math.floor(length / 10) < 0 ? 1 : start - Math.floor(length / 10);
        $scope.end = end + Math.floor(length/10) > $scope.chromosomeSize ? $scope.chromosomeSize : end + Math.floor(length/10);
        $scope.chr = chr;
        $scope.genome = $filter('urlencodeSpecies')(genome);
        $scope.domain = $scope.genoverseUtils.getEnsemblSubdomainByDivision($scope.genome, $scope.genoverseUtils.genomes);
    };


    /**
     * Copy to clipboard buttons allow the user to copy an RNA sequence as RNA or DNA into
     * the clipboard by clicking on them. Buttons are located near the Sequence header.
     */
    $scope.activateCopyToClipboardButtons = function() {
        /**
         * Returns DNA sequence, corresponding to input RNA sequence. =)
         */
        function reverseTranscriptase(rna) {
            // case-insensitive, global replacement of U's with T's
            return rna.replace(/U/ig, 'T');
        }

        var rnaClipboard = new Clipboard('#copy-as-rna', {
            "text": function() {
                var rna = $('#rna-sequence').text();
                rna = rna.replace(/\s/g, '');  // remove whitespace chars (arising due to colored <spans> in sequence)
                return rna;
            }
        });

        var dnaClipbaord = new Clipboard('#copy-as-dna', {
            "text": function() {
                var rna = $('#rna-sequence').text();
                rna = rna.replace(/\s/g, '');  // remove whitespace chars (arising due to colored <spans> in sequence)
                var dna = reverseTranscriptase(rna);
                return dna;
            }
        });
    };

    $scope.fetchRfamHits = function() {
        return $http.get(routes.apiRfamHitsView({upi: $scope.upi}))
    };

    $scope.activateFeatureViewer = function() {
        $(document).ready(function() {
            //Create a new Feature Viewer and add some rendering options
            var options = {
                showAxis: true,
                showSequence: true,
                brushActive: true,
                toolbar:true,
                bubbleHelp: true,
                zoomMax:20
            };

            $scope.featureViewer = new FeatureViewer(
                $scope.rna.sequence,
                "#feature-viewer",
                options
            );

            $scope.fetchRfamHits().then(
                function(response) {
                    data = [];
                    for (var i = 0; i < response.data.results.length; i++) {
                        data.push({
                            x: response.data.results[i].sequence_start,
                            y: response.data.results[i].sequence_stop,
                            description: response.data.results[i].rfam_model.long_name
                        })
                    }

                    $scope.featureViewer.addFeature({
                        data: data,
                        name: "Rfam models",
                        className: "rfamModels",
                        color: "#734639",
                        type: "rect",
                        filter: "type1"
                    });
                },
                function() {
                    console.log('failed to fetch Rfam hits');
                }
            );
        });
    };

    // Initialization
    //---------------

    $scope.activateCopyToClipboardButtons();
    $scope.fetchRna().then(function() {
        $scope.activateFeatureViewer();
    });
};

rnaSequenceController.$inject = ['$scope', '$location', '$window', '$rootScope', '$compile', '$http', '$q', '$filter', 'routes', 'GenoverseUtils'];


/**
 * Configuration function that allows this module to load data
 * from white-listed domains (required for JSONP from ebi.ac.uk).
 * @param $sceDelegateProvider
 */
var sceWhitelist = function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        'self',
        // Allow loading from EBI
        'http://www.ebi.ac.uk/**'
    ]);
};
sceWhitelist.$inject = ['$sceDelegateProvider'];


angular.module("rnaSequence", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'Genoverse'])
    .config(sceWhitelist)
    .controller("rnaSequenceController", rnaSequenceController);
