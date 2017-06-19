var rnaSequenceController = function($scope, $location, $window, $rootScope) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3]; // TODO: this might not exist!

    // programmatically switch tabs
    $scope.activeTab = 0;
    $scope.activateTab = function(index) {
        $scope.activeTab = parseInt(index); // have to convert index to string
    };

    // Downloads tab shouldn't be clickable
    $scope.checkTab = function($event, $selectedIndex) {
        if ($selectedIndex == 3) {
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

    // hopscotch guided tour
    $scope.activateTour = function () {
        hopscotch.startTour($rootScope.tour, 4); // start from step 4
    };

    activateCopyToClipboardButtons();
    activateModifiedNucleotides();

    /**
     * Modified nucleotides visualisation.
     */
    function activateModifiedNucleotides() {
        $('body').on('click', 'button[data-modifications]', function() {
            // destroy any existing popovers before reading in the sequence
            $('.modified-nt').popover('destroy');
            var $pre = $('#rna-sequence'),
                text = $pre.text(),
                modifications = $(this).data('modifications'),
                arrayLength = modifications.length,
                seq_new = '',
                start = 0,
                template = Handlebars.compile($("#handlebars-modified-nt-popover-tmpl").html());

            // loop over modifications and insert span tags with modified nucleotide data
            for (var i = 0; i < arrayLength; i++) {
              seq_new += text.slice(start, modifications[i].position - 1) +
                         template(modifications[i].chem_comp);
              start = modifications[i].position;
            }
            seq_new += text.slice(start, text.length);

            // update the sequence (use `html`, not `text`)
            $pre.html(seq_new);
            // bring sequence in the viewport
            scroll_to_pre();
            // show the entire sequence
            $pre.css({
              'overflow': 'auto',
              'max-height': 'initial',
            });
            // initialize popovers
            $('.modified-nt').popover({
              placement: 'top',
              html: true,
              container: 'body',
              viewport: '#rna-sequence',
            });
            // activate the first popover
            $('.modified-nt').first().focus().popover('show');

            /**
             * Scroll to the sequence.
             */
            function scroll_to_pre() {
              $('html, body').animate({
                  scrollTop: $('pre').offset().top - 100
              }, 1200);
            }
        });
    }

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
                rna = rna.replace(/\s/g, ''); // remove whitespace chars (arising due to colored <spans> in sequence)
                return rna;
            }
        });

        var dnaClipbaord = new Clipboard('#copy-as-dna', {
            "text": function() {
                var rna = $('#rna-sequence').text();
                rna = rna.replace(/\s/g, ''); // remove whitespace chars (arising due to colored <spans> in sequence)
                var dna = reverseTranscriptase(rna);
                return dna;
            }
        });
    };
};

rnaSequenceController.$inject = ['$scope', '$location', '$window', '$rootScope'];



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
