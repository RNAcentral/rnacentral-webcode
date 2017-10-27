var rnaSequenceController = function($scope, $location, $window, $rootScope, $compile, $http, $filter, routes, GenoverseUtils) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3];  // TODO: this might not exist!
    $scope.hide2dTab = true;

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
    }

    // hopscotch guided tour
    $scope.activateTour = function () {
        // hopscotch_tour = new guidedTour;
        // hopscotch_tour.initialize();
        hopscotch.startTour($rootScope.tour, 4);  // start from step 4
    };

    // Modified nucleotides visualisation.
    $scope.activateModifiedNucleotides = function(modifications) {
        // sort modifications by position
        modifications.sort(function(a, b) {return a.position - b.position});

        // destroy any existing popovers before reading in the sequence
        $('.modified-nt').popover('destroy');

        // initialize variables
        var $pre = $('#rna-sequence');
        var text = $pre.text();
        var newText = "";
        var modification;

        // loop over modifications and insert span tags with modified nucleotide data
        var start = 0;
        for (var i = 0; i < modifications.length; i++) {
            newText += text.slice(start, modifications[i].position - 1);

            // create links to pdb and modomics, if possible
            var pdbLink = "", modomicsLink = "";
            if (modifications[i].chem_comp.pdb_url) {
                pdbLink = '<a href=\'' + modifications[i].chem_comp.pdb_url + '\' target=\'_blank\'>PDBe</a> <br>';  // note <br> in the end
            }
            if (modifications[i].chem_comp.modomics_url) {
                modomicsLink = '<a href=\'' + modifications[i].chem_comp.modomics_url + '\' target=\'_blank\'>Modomics</a>';
            }

            // html template for a modified nucleotide
            modification = '<span class="modified-nt" role="button" tabindex="10" ' +
              'data-trigger="focus" ' +
              'data-toggle="popover" ' +
              'data-content="' + modifications[i].chem_comp.description + ' <br> ' + pdbLink + modomicsLink + '" ' +
              'title="Modified nucleotide <strong>' + modifications[i].chem_comp.id + '</strong>">' +
                modifications[i].chem_comp.one_letter_code +
            '</span>';

            newText += modification;

            start = modifications[i].position;  // prepare start position for next iteration
        }
        newText += text.slice(start, text.length);  // last iteration

        // update the sequence (use `html`, not `text`)
        $pre.html(newText);

        // scroll to sequence <pre>, bring sequence in the viewport
        $('html, body').animate(
            { scrollTop: $('#rna-sequence').offset().top - 100 },
            1200
        );

        // initialize popovers
        $('.modified-nt').popover({
            placement: 'top',
            html: true,
            container: 'body',
            viewport: '#rna-sequence',
        });

        // activate the first popover
        $('.modified-nt').first().focus().popover('show');
    };

    // populate data for angular-genoverse instance
    $scope.activateGenomeBrowser = function(start, end, strand, chromosome, species, description, label) {
        $http.get(routes.genomesApi(), { cache: true }).then(  // if genomes've already been loaded, use cache
            function(response) {
                genomes = $scope.genomes = response.data;
                // genome must be a reference to an object in genomes Array, not another object with same value
                $scope.genome = $scope.genomes.filter(function(element) {
                    return element.species.toLowerCase() == species.toLowerCase();
                })[0];
                $scope.start = start;
                $scope.end = end;
                $scope.chromosome = chromosome;

                $scope.genoverseUtils = new GenoverseUtils();

                $scope.urls = {
                    sequence: genoverse.urls.sequence($scope.genome),
                    genes: genoverse.urls.genes($scope.genome),
                    transcripts: genoverse.urls.transcripts($scope.genome),
                    RNAcentral: genoverse.urls.RNAcentral($scope.genome)
                };
                $scope.RNAcentralParseData = genoverse;

            },
            function(response) { console.log("Unable to download available genomes from server!"); return; }
        );
    };


    activateCopyToClipboardButtons();

    /**
     * Copy to clipboard buttons allow the user to copy an RNA sequence as RNA or DNA into
     * the clipboard by clicking on them. Buttons are located near the Sequence header.
     */
    function activateCopyToClipboardButtons() {
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
};

rnaSequenceController.$inject = ['$scope', '$location', '$window', '$rootScope', '$compile', '$http', '$filter', 'routes', 'GenoverseUtils'];


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


angular.module("rnaSequence", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .config(sceWhitelist)
    .controller("rnaSequenceController", rnaSequenceController);
