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

angular.module('rnacentralApp').controller('GenoverseGenomeBrowser', ['$scope', '$location', '$filter', 'GenoverseUtils', function ($scope, $location, $filter, GenoverseUtils) {

    // Variables
    // ---------

    $scope.Genoverse = Genoverse;
    $scope.genoverseUtils = new GenoverseUtils($scope);
    $scope.genomes = genomes;

    $scope.browserLocation = { genome: genome, chromosome: chromosome, start: start, end: end, domain: $scope.genoverseUtils.getEnsemblSubdomainByDivision(genome)};

    $scope.$location = $location;

    // Event handlers
    // --------------

    // handle copy to clipboard button
    new Clipboard('#copy-genome-location', {
        "text": function () {
            return document.location.href;
        }
    });

    // initialize a tooltip on the share button
    $('#copy-genome-location').tipsy();

    // reflect any changes in genome in address bar
    $scope.$watch('browserLocation.genome', setUrl);
    $scope.$watch('browserLocation.chromosome', setUrl);
    $scope.$watch('browserLocation.start', setUrl);
    $scope.$watch('browserLocation.end', setUrl);

    $scope.$watch('genome', setDomain);

    /**
     * Sets the url in address bar to reflect the changes in browser location
     */
    function setUrl(newValue, oldValue) {
        // set the full url
        $location.search({
            species: $scope.browserLocation.genome,  // filter is from Genoverse module
            chromosome: $scope.browserLocation.chromosome,
            start: $scope.browserLocation.start,
            end: $scope.browserLocation.end
        });
        $location.replace();
    }

    /**
     * Change ensembl subdomain upon species change
     */
    function setDomain(newValue, oldValue) {
        $scope.browserLocation.domain = $scope.genoverseUtils.getEnsemblSubdomainByDivision(newValue);
    }
}]);

})();
