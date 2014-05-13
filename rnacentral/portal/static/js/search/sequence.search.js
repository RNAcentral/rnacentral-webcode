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

// RNAcentral sequence search

;rnaMetasearch.controller('SeqResultsListCtrl', function($scope, $http) {

	$scope.query = {
		sequence: '',
		submit_attempted: false,
	};

	$scope.defaults = {
		page_size: 10,
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
		$scope.params.status_message = 'Loading results';

		$http({
			url: $scope.results.url,
			method: 'GET',
			params: {
				page_size: $scope.params.page_size,
				page: 1, // all results on 1 page
			}
		}).success(function(data){
			console.log('Results retrieved');
			console.log(data);
			$scope.results.count = data.results.count;
			$scope.results.ena_count = data.results.ena_count;
			$scope.results.alignments = data.results.alignments;
			$scope.params.search_in_progress = false;
			$scope.params.status_message = 'Done';
		}).error(function(){
			$scope.params.search_in_progress = false;
			$scope.params.status_message = 'Error';
			// todo
		});
	};

    /**
     * Poll job status in regular intervals.
     */
	var poll_job_status = function(url) {
		$scope.params.status_message = 'Waiting for results';
		var polling_interval = 1000; // milliseconds
		var interval = setInterval(function(){
			console.log('Checking status');
			$http({
				url: url,
				method: 'GET'
			}).success(function(data){
				if (data.status === 'Done') {
					console.log('Results ready');
					window.clearInterval(interval);
					// get results
					$scope.results.url = data.url;
					get_results();
				}
			}).error(function(){
				$scope.params.status_message = 'Error';
			});
		}, polling_interval);
	};

    /**
     * Initiate sequence search.
     */
	var search = function(sequence) {
		$scope.params.search_in_progress = true;
		$scope.params.status_message = 'Submitting query';
		$http({
			url: '/api/v1/sequence-search/submit?sequence=' + sequence,
			method: 'GET', // todo: switch to POST
		}).success(function(data) {
			console.log(data);
			poll_job_status(data.url);
		}).error(function(data, status) {
			$scope.params.error_message = data.message;
			$scope.params.status_message = 'Error';
			console.log(data);
			console.log(status);
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
		$scope.params.status_message = 'Loading more results';
        get_results();
    };

    /**
     * Calculate how many items are visible.
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
			ena_count: 0,
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
		$('textarea').focus();
	};

    /**
     * Launch the search from template.
     */
	$scope.sequence_search = function(sequence) {
		$scope.query.sequence = sequence;
		search($scope.query.sequence);
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

	(function(){
		$('body').tooltip({
			selector: '.help',
			delay: { show: 200, hide: 100 }
		});
	})();

});
