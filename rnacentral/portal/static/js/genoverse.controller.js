/*
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

(function() {

angular.module('rnacentralApp').controller('GenoverseGenomeBrowser', ['$scope', '$location', '$filter', function ($scope, $location, $filter) {

    /* Constructor */
    $scope.genomes = genomes;
    // from JS standpoint, genome and genomes[i] == genome are different objects, but we want exactly the same, so:
    $scope.genome = genomes.filter(function(element) {
        return element.species.toLowerCase() == genome.species.toLowerCase();
    })[0];
    $scope.chromosome = chromosome;
    $scope.start = start;
    $scope.end = end;
    $scope.strand = 1;
    $scope.description = '';

    // handle copy to clipboard button
    new Clipboard('#copy-genome-location', {
        "text": function () {
            return document.location.href;
        }
    });

    // initialize a tooltip on the share button
    $('#copy-genome-location').tooltip();

    // reflect any changes in genome/chromosome/start/end in address bar
    $scope.$watch('genome', setUrl);
    $scope.$watch('chromosome', setUrl);
    $scope.$watch('start', setUrl);
    $scope.$watch('end', setUrl);


    // Method definitions
    // ------------------

    /**
     * Sets the url in address bar to reflect the changes in browser location
     */
    function setUrl(newValue, oldValue) {
        // set the full url
        $location.path("/genome-browser/" + $filter('urlencodeSpecies')($scope.genome.species));
        $location.search({chromosome: $scope.chromosome, start: $scope.start, end: $scope.end});
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
        var species = species.val().replace(/ /g, '-');

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
            var urlBeginning = pathElements.slice(0, pathElements.length - 1);
            var urlEnding = pathElements.slice(-1)[0];

            if (urlEnding != species) {
                urlBeginning.push(species);
                var newPathname = urlBeginning.join("/");
                if (hasTrailingSlash) {
                    newPathname = newPathname + "/";
                }
                history.pushState({}, document.title, newPathname + "?" + searchParams);
            }
        }
    }
}]);

})();