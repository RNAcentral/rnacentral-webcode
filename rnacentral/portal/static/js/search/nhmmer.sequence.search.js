/*
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

/**
 * Angular.js app for RNAcentral sequence search.
 */

/**
 * Create AngularJS app.
 */
angular.module('nhmmerSearch', ['chieffancypants.loadingBar', 'ngAnimate']);

/**
 * Main controller.
 */
;angular.module('rnacentralApp').controller('NhmmerResultsListCtrl', ['$scope', '$http', '$timeout', '$location', function($scope, $http, $timeout, $location) {

    $scope.query = {
        sequence: '',
        submit_attempted: false,
    };

    $scope.defaults = {
        page_size: 10,
        min_length: 20,
        submit_endpoint: '/sequence-search-new/submit-query',
        results_endpoint: '/sequence-search-new/get-results',
        messages: {
            get_results: 'Loading results',
            done: 'Done',
            failed: 'Error',
            submit_failed: 'There was a problem submitting your query. Please try again later or get in touch if the error persists.',
            results_failed: 'There was a problem retrieving the results. Please try again later or get in touch if the error persists.',
            poll_job_status: 'Waiting for results',
            submitting: 'Submitting query',
            loading_more_results: 'Loading more results',
            too_short: 'The sequence cannot be shorter than 20 nucleotides',
        },
    };

    $scope.params = {
        search_in_progress: false,
        page_size: $scope.defaults.page_size,
        error_message: '',
        status_message: '',
        show_alignments: true,
    };

    $scope.results = results_init();

    /**
     * Retrieve results given a results url.
     */
    var get_results = function(id, next_page) {
        $scope.params.search_in_progress = true;
        $scope.params.status_message = $scope.defaults.messages.get_results;
        next_page = next_page || false;

        $http({
            url: next_page ? $scope.results.next_page : $scope.defaults.results_endpoint,
            method: 'GET',
            params: {
                id: id,
            },
        }).success(function(data){
            $scope.results.count = data.count;
            $scope.results.alignments = $scope.results.alignments.concat(data.results);
            $scope.results.next_page = data.next;
            $scope.params.search_in_progress = false;
            $scope.params.status_message = $scope.defaults.messages.done;
        }).error(function(){
            $scope.params.search_in_progress = false;
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
        });
    };

    /**
     * Poll job status in regular intervals.
     */
    var poll_job_status = function(url) {
        $scope.params.status_message = $scope.defaults.messages.poll_job_status;
        var polling_interval = 1000; // milliseconds
        var interval = setInterval(function(){
            $http({
                url: url,
                method: 'GET'
            }).success(function(data){
                if (data.status === 'finished') {
                    window.clearInterval(interval);
                    // get results
                    get_results(data.id);
                } else if (data.status === 'failed') {
                    window.clearInterval(interval);
                    $scope.params.status_message = $scope.defaults.messages.failed;
                    $scope.params.error_message = $scope.defaults.messages.results_failed;
                }
            }).error(function(){
                $scope.params.status_message = $scope.defaults.messages.failed;
                $scope.params.error_message = $scope.defaults.messages.results_failed;
            });
        }, polling_interval);
    };

    /**
     * Initiate sequence search.
     */
    var search = function(sequence) {
        $scope.results = results_init();
        sequence = parse_fasta(sequence);
        if (!is_valid_sequence()) {
            return;
        }
        $scope.params.search_in_progress = true;
        $scope.params.error_message = '';
        $scope.params.status_message = $scope.defaults.messages.submitting;
        $http({
            url: $scope.defaults.submit_endpoint,
            method: 'POST',
            data: $.param({q: sequence}),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        }).success(function(data) {
            // save query id
            $scope.results.id = data.id;
            // update url
            $location.search({'id': data.id});
            // begin polling for results
            $timeout(function() {
                poll_job_status(data.url);
            }, 1000);
        }).error(function(data, status) {
            $scope.params.error_message = $scope.defaults.messages.submit_failed;
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.search_in_progress = false;
        });

        /**
         * Check sequence length once the fasta header line is removed.
         */
        function is_valid_sequence() {
            if (sequence.length < $scope.defaults.min_length) {
                $scope.params.error_message = $scope.defaults.messages.too_short;
                $scope.params.status_message = $scope.defaults.messages.failed;
                return false;
            } else {
                return true;
            }
        }
    };

    /**
     * Public method for submitting the query.
     */
    $scope.submit_query = function() {
        $scope.query.submit_attempted = true;
        if (!$scope.seqQueryForm.$valid) {
            return;
        }
        search($scope.query.sequence);
    };

    /**
     * Load more results.
     */
    $scope.load_more_results = function() {
        var next_page = true;
        get_results($scope.results.id, next_page);
    };

    /**
     * Initialize results object.
     */
    function results_init() {
        return {
            id: null,
            alignments: [],
            count: null,
            next_page: null,
        };
    }

    /**
     * Reset the form.
     */
    $scope.reset = function() {
        $location.search('id', null);
        $scope.query.sequence = '';
        $scope.query.submit_attempted = false;
        $scope.results = results_init();
        $scope.params.status_message = '';
        $scope.params.page_size = $scope.defaults.page_size;
        $('textarea').focus();
    };

    /**
     * Launch the search from template.
     */
    $scope.sequence_search = function(sequence) {
        $scope.query.sequence = sequence;
        search(sequence);
    };

    /**
     * Format e_value.
     */
    $scope.format_evalue = function(e_value) {
        return parseFloat(e_value).toExponential(2);
    };

    /**
     * Toggle alignments button.
     */
    $scope.toggle_alignments = function() {
        $scope.params.show_alignments = !$scope.params.show_alignments;
        $('#toggle-alignments').text(function(i, text){
          return text === "Show alignments" ? "Hide alignments" : "Show alignments";
        });
    };

    /**
     * Remove fasta header and spaces and newlines.
     */
    function parse_fasta(sequence) {
        return sequence.replace(/^>.+?[\n\r]/, '').replace(/\s/g, '');
    }

    /**
     * When the controller is first created:
     * - activate Bootstrap tooltips when the controller is created.
     * - retrieve search results if necessary
     */
    (function(){
        if ($location.url().indexOf("?id=") > -1) {
            get_results($location.search().id);
        }

        $('body').tooltip({
            selector: '.help',
            delay: { show: 200, hide: 100 },
            container: 'body',
        });
    })();

}]);
