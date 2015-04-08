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
        polling_interval: 5000, // milliseconds

        // global variables defined in the Django template
        min_length: SEQ_SEARCH_PARAMS.min_length,
        submit_endpoint: SEQ_SEARCH_PARAMS.submit_endpoint,
        job_status_endpoint: SEQ_SEARCH_PARAMS.job_status_endpoint,
        results_endpoint: SEQ_SEARCH_PARAMS.results_endpoint,
        query_info_endpoint: SEQ_SEARCH_PARAMS.query_info_endpoint,
        md5_endpoint: SEQ_SEARCH_PARAMS.md5_endpoint,

        messages: {
            get_results: 'Loading results',
            done: 'Done',
            failed: 'Error',
            submit_failed: 'There was a problem submitting your query. Please try again later or get in touch if the error persists.',
            results_failed: 'There was a problem retrieving the results. Please try again later or get in touch if the error persists.',
            poll_job_status: 'Waiting for results',
            submitting: 'Submitting query',
            loading_more_results: 'Loading more results',
            too_short: 'The sequence cannot be shorter than ' + SEQ_SEARCH_PARAMS.min_length + ' nucleotides',
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
     * Check job status using REST API.
     */
    var check_job_status = function(id, interval) {
        interval = interval || null;
        $http({
            url: $scope.defaults.job_status_endpoint,
            method: 'GET',
            params: {
                id: id,
            },
        }).success(function(data){
            if (data.status === 'finished') {
                if (interval) {
                    window.clearInterval(interval);
                }
                get_results(data.id);
            } else if (data.status === 'failed') {
                if (interval) {
                    window.clearInterval(interval);
                }
                $scope.params.status_message = $scope.defaults.messages.failed;
                $scope.params.error_message = $scope.defaults.messages.results_failed;
            }
        }).error(function(){
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
        });
    };

    /**
     * Poll job status at regular intervals.
     */
    var poll_job_status = function(id) {
        $scope.params.status_message = $scope.defaults.messages.poll_job_status;
        var interval = setInterval(function(){
            check_job_status(id, interval);
        }, $scope.defaults.polling_interval);
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
                poll_job_status(data.id);
            }, $scope.defaults.polling_interval);
        }).error(function(data, status) {
            $scope.params.error_message = $scope.defaults.messages.submit_failed;
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.search_in_progress = false;
        });

        retrieve_exact_match(sequence);

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
            exact_match: null,
        };
    }

    /**
     * Use RNAcentral API to retrieve an exact match
     * to the query sequence.
     */
    function retrieve_exact_match(sequence) {
        sequence = parse_fasta(sequence);
        var md5_hash = md5(sequence.toUpperCase().replace(/U/g, 'T'));
        var url = $scope.defaults.md5_endpoint + '?md5=' + md5_hash;
        $http({
            url: url,
            method: 'GET',
            params: {
                md5: md5_hash,
            }
        }).success(function(data) {
            if (data.count > 0) {
                $scope.results.exact_match = data.results[0].rnacentral_id;
            }
        });
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
     * Retrieve query information in order to load
     * the query sequence into the search box.
     */
    function get_query_info(query_id) {
        $http({
            url: $scope.defaults.query_info_endpoint,
            method: 'GET',
            params: {
                id: query_id,
            },
        }).success(function(data) {
            $scope.query.sequence = data.sequence;
            retrieve_exact_match(data.sequence);
        }).error(function(){
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
        });
    }

    /**
     * When the controller is first created:
     * - activate Bootstrap tooltips when the controller is created.
     * - retrieve search results if necessary
     */
    (function(){
        if ($location.url().indexOf("?id=") > -1) {
            poll_job_status($location.search().id);
            get_query_info($location.search().id);
        }

        $('body').tooltip({
            selector: '.help',
            delay: { show: 200, hide: 100 },
            container: 'body',
        });
    })();

}]);
