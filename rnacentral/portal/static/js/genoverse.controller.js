angular.module('rnacentralApp').controller('GenoverseGenomeBrowser', ['$scope', '$location', function($scope, $location) {

    /* Constructor */

    $scope.browser = {};
    $scope.browser.genome = genome;
    $scope.browser.chromosome = chromosome;
    $scope.browser.start = start;
    $scope.browser.end = end;

    // handle form submit button
    $('#genome-display').on('click', showGenome);

    // handle copy to clipboard button
    new Clipboard('#copy-genome-location', {
        "text": function() {
            return document.location.href;
        }
    });

    showGenome();

    // Listen to global browser object.
    // Note: third argument (true) means that we require objectEquality, not just referentialEquality
    $scope.$watch(browser, function(newValue, oldValue, scope) { scope.browser = newValue; }, true);


    /* Method definitions */

    /**
     * Show genome location using Genoverse.
     * Create a hidden button with data attributes and trigger the click event.
     * Update coordinates in the user interface.
     */
    function showGenome() {
        // delete previous instance of browser completely
        $('.genoverse-xref').remove();
        delete window.browser;

        // get species name with whitespaces replaced with hyphens, handle dog as a special case
        var species = $scope.browser.genome.species;
        if (species == 'Canis familiaris') { species = 'Canis lupus familiaris'; }
        species = species.replace(/ /g,'_').toLowerCase();

        // set all data attributes and initialize plugin by clicking invisible button
        $('<button class="genoverse-xref"></button>').
            hide().
            appendTo('.genoverse-wrap').
            data('chromosome', $scope.chromosome).
            data('genomic-start', $scope.start).
            data('genomic-end', $scope.end).
            data('strand', 1).
            data('species', species).
            data('description', '').
            data('species-label', $scope.browser.genome.species).
            click(); // this initializes plugin
    }

    /**
    * Show Ensembl and UCSC links for the currently displayed region.
    */
    function updateExternalLinks(){
        var option = species.find('option:selected'),
            division = option.data('division'),
            ucsc_db = option.data('ucsc-db'),
            ucsc = $('.ucsc-link'),
            domain = '',
            ucsc_chr = '',
            url = '';

        if (division == 'Ensembl') {
            domain = 'http://ensembl.org/';
        } else if (division == 'Ensembl Plants') {
            domain = 'http://plants.ensembl.org/';
        } else if (division == 'Ensembl Metazoa') {
            domain = 'http://metazoa.ensembl.org/';
        } else if (division == 'Ensembl Bacteria') {
            domain = 'http://bacteria.ensembl.org/';
        } else if (division == 'Ensembl Fungi') {
            domain = 'http://fungi.ensembl.org/';
        } else if (division == 'Ensembl Protists') {
            domain = 'http://protists.ensembl.org/';
        }

        // update Ensembl link
        url = domain + species.val().replace(/ /g,'_') + '/Location/View?r=' + browser.chr + ':' + browser.start + '-' + browser.end;
        $('#ensembl-link').attr('href', url).text(division);

        // update UCSC link if UCSC assembly is available
        if (ucsc_db) {
            if (browser.chr.match(/^\d+$|^[XY]$/)) {
                ucsc_chr = 'chr' + browser.chr;
            }
            else {
                ucsc_chr = browser.chr;
            }
            url = 'http://genome.ucsc.edu/cgi-bin/hgTracks?db='+ ucsc_db +'&position=' + ucsc_chr + '%3A' + browser.start + '-' + browser.end;
            ucsc.show().find('a').attr('href', url);
        }
        else {
            ucsc.hide();
        }
    }

    /**
     * Synchronize coordinates in Genoverse, in address bar, in form inputs and in the text line
     * above genoverse genome browser.
     *
     * We need to find out, which one was actually changed by the user since last run and modify
     * the others.
     */
    function updateCoordinates() {
        // update form start/end inputs
        start.val(browser.start);
        end.val(browser.end);

        // update location string right above genoverse
        var species = $('#genomic-species-select');
        text = '<em>' + species.val() + '</em>' + ' ' + browser.chr + ':' + browser.start + '-' + browser.end;
        if ($('#genomic-location').html() != text) {
            $('#genomic-location').html(text);
        }

        // update get param in browser, if they changed
        var searchParams = "chromosome=" + browser.chr;
        searchParams = searchParams.concat("&start=" + browser.start);
        searchParams = searchParams.concat("&end=" + browser.end);

        if (document.location.search != searchParams) {
            history.pushState({}, document.title, document.location.pathname + "?" + searchParams);
        }

        // update url if species changed
        var species = species.val().replace(/ /g,'-');

        var pathname = document.location.pathname;
        var hasTrailingSlash = false;
        if (document.location.pathname.substr(-1) === '/') {
            hasTrailingSlash = true;
            pathname = document.location.pathname.substr(0, document.location.pathname.length - 1);
        }

        if (document.location.pathname.search(/genome-browser\/.+/) == -1) { // if url is like genome-browser/smth.
            var newPathname = pathname + "/" + species;
            if (hasTrailingSlash) { newPathname = newPathname + "/"; }
            history.pushState({}, document.title, newPathname + "?" + searchParams);
        }
        else { // if url is like /genome-browser/homo-sapiens
            var pathElements = pathname.split("/");
            var urlBeginning = pathElements.slice(0, pathElements.length-1);
            var urlEnding = pathElements.slice(-1)[0];

            if (urlEnding != species) {
                urlBeginning.push(species);
                var newPathname = urlBeginning.join("/");
                if (hasTrailingSlash) { newPathname = newPathname + "/"; }
                history.pushState({}, document.title, newPathname + "?" + searchParams);
            }
        }
    }
}]);