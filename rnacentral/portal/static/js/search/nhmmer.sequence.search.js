/*
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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
;angular.module('rnacentralApp').controller('NhmmerResultsListCtrl', ['$scope', '$http', '$timeout', '$location', '$q', '$window', function($scope, $http, $timeout, $location, $q, $window) {

    $scope.query = query_init();

    $scope.defaults = {
        polling_interval: 1000, // milliseconds

        // global variables defined in the Django template
        min_length: SEQ_SEARCH_PARAMS.min_length,
        submit_endpoint: SEQ_SEARCH_PARAMS.submit_endpoint,
        job_status_endpoint: SEQ_SEARCH_PARAMS.job_status_endpoint,
        results_endpoint: SEQ_SEARCH_PARAMS.results_endpoint,
        query_info_endpoint: SEQ_SEARCH_PARAMS.query_info_endpoint,
        md5_endpoint: SEQ_SEARCH_PARAMS.md5_endpoint,
        cancel_job_endpoint: SEQ_SEARCH_PARAMS.cancel_job_endpoint,

        messages: {
            get_results: 'Loading results',
            done: 'Done',
            failed: 'Error',
            submit_failed: 'There was a problem submitting your query. Please try again later or get in touch if the error persists.',
            job_failed: 'There was a problem with your query. Please try again later or get in touch if the error persists.',
            results_failed: 'There was a problem retrieving the results. Please try again later or get in touch if the error persists.',
            cancelled: 'The search was cancelled',
            queued: 'Queued',
            started: 'Running',
            poll_job_status: 'Waiting for results',
            submitting: 'Submitting query',
            loading_more_results: 'Loading more results',
            too_short: 'The sequence cannot be shorter than ' + SEQ_SEARCH_PARAMS.min_length + ' nucleotides',
        },
    };

    $scope.ordering = [
        { sort_field: 'e_value', label: 'E-value (min to max) - default'},
        { sort_field: '-e_value', label: 'E-value (max to min)'},
        { sort_field: '-identity', label: 'Identity (max to min)' },
        { sort_field: 'identity', label: 'Identity: (min to max)' },
        { sort_field: '-query_coverage', label: 'Query coverage: (max to min)' },
        { sort_field: 'query_coverage', label: 'Query coverage: (min to max)' },
        { sort_field: '-target_coverage', label: 'Target coverage: (max to min)' },
        { sort_field: 'target_coverage', label: 'Target coverage: (min to max)' },
    ];

    $scope.params = {
        search_in_progress: false,
        error_message: '',
        status_message: '',
        show_alignments: true,
        selectedOrdering: $scope.ordering[0],
        initial_page_size: null,
    };

    $scope.results = results_init();

    var timeout;

    /**
     * Update the `ordering` url parameter
     * based on the current user selection.
     */
    $scope.update_ordering = function() {
        $location.search($.extend($location.search(), {
            ordering: $scope.params.selectedOrdering.sort_field,
        }));
    };

    /**
     * Update the `page_size` url parameter
     * based on the number of currently loaded alignments.
     */
    var update_page_size = function() {
        $location.search($.extend($location.search(), {
            page_size: $scope.results.alignments.length,
        }));
    };

    /**
     * Retrieve results given a results url.
     */
    $scope.get_results = function(id, next_page) {
        $scope.params.search_in_progress = true;
        $scope.params.status_message = $scope.defaults.messages.get_results;
        id = id || $location.search().id;
        next_page = next_page || false;

        $http({
            url: next_page ? $scope.results.next_page : $scope.defaults.results_endpoint,
            method: 'GET',
            params: {
                id: id,
                ordering: $scope.params.selectedOrdering.sort_field + ',result_id',
                page_size: $scope.params.initial_page_size || 10,
            },
        }).success(function(data){
            $scope.results.count = data.count;
            if (next_page) {
                $scope.results.alignments = $scope.results.alignments.concat(data.results);
            } else {
                $scope.results.alignments = data.results;
            }
            if ($scope.params.initial_page_size) {
                $scope.params.initial_page_size = null;
            }
            $scope.results.next_page = data.next;
            $scope.params.search_in_progress = false;
            $scope.params.status_message = $scope.defaults.messages.done;
            update_page_size();
            update_page_title();
        }).error(function(){
            $scope.params.search_in_progress = false;
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
            update_page_title();
        });
    };

    /**
     * Cancel remote job and stop polling for results.
     */
     $scope.cancel_job = function(){
        clearTimeout(timeout);
        $http({
            url: $scope.defaults.cancel_job_endpoint,
            method: 'GET',
            params: {
                id: $location.search().id,
            },
        }).success(function(){
            $scope.params.search_in_progress = false;
            $scope.params.status_message = $scope.defaults.messages.cancelled;
            update_page_title();
        });
     };

    /**
     * Check job status using REST API.
     */
    var check_job_status = function(id) {
        $http({
            url: $scope.defaults.job_status_endpoint,
            method: 'GET',
            params: {
                id: id,
            },
            ignoreLoadingBar: true,
        }).success(function(data){
            $scope.query.ended_at = moment(data.ended_at).utc();
            $scope.query.enqueued_at = moment(data.enqueued_at).utc();
            if (data.status === 'finished') {
                $scope.get_results(data.id);
            } else if (data.status === 'failed') {
                $scope.params.search_in_progress = false;
                $scope.params.status_message = $scope.defaults.messages.failed;
                $scope.params.error_message = $scope.defaults.messages.job_failed;
                update_page_title();
            } else {
                $scope.params.search_in_progress = true;
                if (data.status === 'queued') {
                    $scope.params.status_message = $scope.defaults.messages.queued;
                } else if (data.status === 'started') {
                    $scope.params.status_message = $scope.defaults.messages.started;
                } else {
                    $scope.params.status_message = '';
                }
                timeout = setTimeout(function() {
                    check_job_status(id);
                    update_page_title();
                }, $scope.defaults.polling_interval);
            }
        }).error(function(){
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
        });
    };

    /**
     * Get current time.
     */
    $scope.get_time_elapsed = function() {
        return moment().diff($scope.query.enqueued_at);
    }

    /**
     * Initiate sequence search.
     */
    var search = function(sequence) {
        $scope.results = results_init();

        var deferred = $q.defer();
        var promise = deferred.promise;
        promise = promise.then(parse_rnacentral_id).then(run_search);
        deferred.resolve(sequence);

        /**
         * Retrieve sequence given an RNAcentral id using promises.
         */
        function parse_rnacentral_id(sequence) {
            var deferred = $q.defer();
            if (sequence.match(/^URS[A-Fa-f0-9]{10}$/i)) {
                $http({
                    url: $scope.defaults.md5_endpoint + '/' + sequence,
                }).success(function(data){
                    $scope.query.sequence = '>' + data.rnacentral_id + '\n' + data.sequence;
                    deferred.resolve($scope.query.sequence);
                });
            } else {
                deferred.resolve(sequence);
                return deferred.promise;
            }
            return deferred.promise;
        }

        /**
         * Submit query and begin checking whether the results
         * are ready.
         */
        function run_search(sequence) {
            input = parse_input(sequence);
            if (!is_valid_sequence(input.sequence)) {
                return;
            }
            $scope.params.search_in_progress = true;
            $scope.params.error_message = '';
            $scope.params.status_message = $scope.defaults.messages.submitting;

            retrieve_exact_match(sequence);

            return $http({
                url: $scope.defaults.submit_endpoint,
                method: 'POST',
                data: $.param({
                    q: input.sequence,
                    description: input.description,
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            }).success(function(data) {
                // save query id
                $scope.results.id = data.id;
                // update url
                $location.search({'id': data.id});
                // begin polling for results
                check_job_status(data.id);
                update_page_title();
            }).error(function(data, status) {
                $scope.params.error_message = $scope.defaults.messages.submit_failed;
                $scope.params.status_message = $scope.defaults.messages.failed;
                $scope.params.search_in_progress = false;
                update_page_title();
            });
        }

        /**
         * Check sequence length once the fasta header line is removed.
         */
        function is_valid_sequence(sequence) {
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
        $scope.get_results($scope.results.id, next_page);
    };

    /**
     * Scroll page to the top.
     */
    $scope.scroll_to_top = function() {
        $("html, body").animate({ scrollTop: "0px" });
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
     * Initialize query object.
     */
    function query_init() {
        return {
            sequence: '',
            submit_attempted: false,
            enqueued_at: moment(null).utc(),
            ended_at: moment(null).utc(),
        };
    }

    /**
     * Use RNAcentral API to retrieve an exact match
     * to the query sequence.
     */
    function retrieve_exact_match(sequence) {
        input = parse_input(sequence);
        var md5_hash = md5(input.sequence.toUpperCase().replace(/U/g, 'T'));
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
        $location.search({});
        $scope.params.search_in_progress = false;
        $scope.query = query_init();
        $scope.results = results_init();
        $scope.params.status_message = '';
        $scope.params.error_message = '';
        $('textarea').focus();
        update_page_title();
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
        $('#toggle-alignments').html(function(i, text){
          var icon = '<i class="fa fa-align-justify"></i> ';
          return icon + (text.indexOf("Show alignments") > -1 ? "Hide alignments" : "Show alignments");
        });
    };

    /**
     * Calculate query sequence length
     * (without whitespace and fasta header).
     */
    $scope.get_query_length = function() {
        var text = document.getElementById("query-sequence").value;
        if (text.match(/^URS[A-Fa-f0-9]{10}$/)) {
            return 0;
        }
        input = parse_input(text);
        return input.sequence.length || 0;
    };

    /**
     * Reverse the query sequence in place and repeat the search.
     * This is helpful when the user accidentally types the sequence in 3' to 5' direction.
     */
    $scope.reverse_and_repeat_search = function() {
        var input = parse_input($scope.query.sequence);
        var reversed_sequence = input.sequence.split("").reverse().join("");
        var description_line = '';
        if (input.description) {
          description_line = '>' + input.description + '\n';
        }
        $scope.query.sequence = description_line + reversed_sequence;
        search($scope.query.sequence);
    };

    /**
     * Parse fasta header, remove whitespace characters.
     */
    function parse_input(sequence) {
        var match = /(^>(.+)[\n\r])?([\s\S]+)/.exec(sequence);
        if (match) {
            return {
                description: match[2] || '',
                sequence: match[3].replace(/\s/g, ''),
            };
        } else {
            return {
                sequence: '',
                description: '',
            };
        }
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
            if (data.description) {
                $scope.query.sequence = '>' + data.description + '\n' + data.sequence;
            } else {
                $scope.query.sequence = data.sequence;
            }
            $scope.query.enqueued_at = moment(data.enqueued_at).utc();
            $scope.query.ended_at = moment(data.ended_at).utc();
            retrieve_exact_match(data.sequence);
        }).error(function(){
            $scope.params.status_message = $scope.defaults.messages.failed;
            $scope.params.error_message = $scope.defaults.messages.results_failed;
        });
    }

    /**
     * Set results ordering based on the url parameter.
     */
    function initialize_ordering() {
        if ($location.search().ordering) {
            var ordering = $location.search().ordering;
            for (var i=0, len=$scope.ordering.length; i < len; i++) {
                if ($scope.ordering[i].sort_field === ordering) {
                    $scope.params.selectedOrdering = $scope.ordering[i];
                }
            }
        }
    }

    /**
     * Show progress in page title.
     */
    function update_page_title() {
        if ($scope.params.status_message === $scope.defaults.messages.failed) {
            $window.document.title = 'Search failed';
        } else if ($scope.params.search_in_progress) {
            $window.document.title = 'Searching...';
        } else if ($scope.params.status_message === $scope.defaults.messages.done) {
            $window.document.title = 'Search done';
        } else {
            $window.document.title = 'Sequence search';
        }
    }

    /**
     * Add standard Javascript isNaN function to the scope
     * so that it can be used in the template.
     */
    $scope.isNaN = isNaN;

    /**
     * When the controller is first created:
     * - activate Bootstrap tooltips when the controller is created.
     * - retrieve search results if necessary
     */
    (function(){
        if ($location.url().indexOf("id=") > -1) {
            // load results
            initialize_ordering();
            $scope.results.id = $location.search().id;
            check_job_status($location.search().id);
            get_query_info($location.search().id);
            $scope.params.initial_page_size = $location.search().page_size || null;
        } else if ($location.search().q) {
            // start sequence search
            $scope.query.sequence = $location.search().q;
            search($scope.query.sequence);
        }

        $('body').tooltip({
            selector: '.help',
            delay: { show: 200, hide: 100 },
            container: 'body',
        });
    })();

}]);
