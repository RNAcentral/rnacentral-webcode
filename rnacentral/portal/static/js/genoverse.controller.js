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

    // handle copy to clipboard button
    new Clipboard('#copy-genome-location', {
        "text": function () {
            return document.location.href;
        }
    });

    // initialize a tooltip on the share button
    $('#copy-genome-location').tooltip();

    // reflect any changes in genome in address bar
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
        $location.path("/genome-browser/" + $filter('urlencodeSpecies')($scope.genome.species)); // this filter's from Genoverse module
        $location.search({chromosome: $scope.chromosome, start: $scope.start, end: $scope.end});
        $location.replace();
    }

}]);

})();
