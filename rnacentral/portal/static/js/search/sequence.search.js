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

;rnaMetasearch.controller('SeqResultsListCtrl', function($scope, $http) {

	$scope.query = {
		sequence: '',
		submit_attempted: false,
	};

	$scope.defaults = {
		page_size: 10,
		submit_endpoint: '/api/v1/sequence-search/submit',
		messages: {
			get_results: 'Loading results',
			done: 'Done',
			failed: 'Error',
			submit_failed: 'There was a problem submitting your query. Please try again later or get in touch if the error persists.',
			results_failed: 'There was a problem retrieving the results. Please try again later or get in touch if the error persists.',
			poll_job_status: 'Waiting for results',
			submitting: 'Submitting query',
			loading_more_results: 'Loading more results',
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
     * Retrive results given a results url.
     */
	var get_results = function() {
		$scope.params.search_in_progress = true;
		$scope.params.status_message = $scope.defaults.messages.get_results;

		$http({
			url: $scope.results.url,
			method: 'GET',
			params: {
				page_size: $scope.params.page_size,
				page: 1, // all results are always on 1 page
			}
		}).success(function(data){
			$scope.results.count = data.results.count;
			$scope.results.alignments = data.results.alignments;
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
				if (data.status === 'Done') {
					window.clearInterval(interval);
					// get results
					$scope.results.url = data.url;
					get_results();
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
		$scope.query.sequence = sequence.replace(/\s/g, '');
		$scope.params.search_in_progress = true;
		$scope.params.status_message = $scope.defaults.messages.submitting;
		$http({
			url: $scope.defaults.submit_endpoint,
			method: 'POST',
			params: {sequence: sequence},
		}).success(function(data) {
			poll_job_status(data.url);
		}).error(function(data, status) {
			$scope.params.error_message = $scope.defaults.messages.submit_failed;
			$scope.params.status_message = $scope.defaults.messages.failed;
			$scope.params.search_in_progress = false;
		});
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
        $scope.params.page_size += $scope.defaults.page_size;
		$scope.params.status_message = $scope.defaults.messages.loading_more_results;
        get_results();
    };

    /**
     * Calculate how many items are currently visible.
     */
    $scope.displayed_items = function() {
        return Math.min($scope.params.page_size, $scope.results.count);
    };

    /**
     * Initialize results object.
     */
	function results_init() {
		return {
			alignments: [],
			count: null,
			url: '',
		}
	};

    /**
     * Reset the form.
     */
    $scope.reset = function() {
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
     * Count the number of gaps in `formatted_alignment`.
     */
	$scope.count_gaps = function(formatted_alignment) {
		return (formatted_alignment.match(/-/g)||[]).length;
	};

    /**
     * Activate Bootstrap tooltips when the controller is created.
     */
	(function(){
		$('body').tooltip({
			selector: '.help',
			delay: { show: 200, hide: 100 },
			container: 'body',
		});
	})();

});
