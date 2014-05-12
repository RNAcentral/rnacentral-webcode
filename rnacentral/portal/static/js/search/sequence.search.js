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

	var default_page_size = 10;

	$scope.query = {
		sequence: '',
		failed: false
	};
	$scope.results = [];
	$scope.count = 0;
	$scope.ena_count = 0;
	$scope.search_in_progress = false;
	$scope.results_urls = '';
	$scope.page_size = default_page_size;
	$scope.error_message = '';

    /**
     * Retrive results given a results url.
     */
	var get_results = function() {
		$scope.search_in_progress = true;

		$http({
			url: $scope.results_url,
			method: 'GET',
			params: {
				page_size: $scope.page_size,
				page: 1,
			}
		}).success(function(data){
			console.log('Results retrieved');
			console.log(data);
			$scope.count = data.results.count;
			$scope.ena_count = data.results.ena_count;
			$scope.results = data.results;
			$scope.search_in_progress = false;
		}).error(function(){
			$scope.search_in_progress = false;
			// todo
		});
	};

    /**
     * Poll job status in regular intervals.
     */
	var poll_job_status = function(url) {
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
					$scope.results_url = data.url;
					get_results();
				}
			}).error(function(){
				// todo
			});
		}, polling_interval);
	};

    /**
     * Initiate sequence search.
     */
	var search = function(sequence) {
		$scope.search_in_progress = true;
		$http({
			url: '/api/v1/sequence-search/submit?sequence=' + sequence,
			method: 'GET', // todo: switch to POST
		}).success(function(data) {
			console.log(data);
			poll_job_status(data.url);
		}).error(function(data, status) {
			$scope.error_message = data.message;
			console.log(data);
			console.log(status);
			$scope.search_in_progress = false;
		});
	};

    /**
     * Public method for submitting the query.
     */
    $scope.submit_query = function() {
    	if (!$scope.seqQueryForm.$valid) {
    		$scope.query.failed = true;
    		return;
    	}
    	$scope.query.failed = false;
        search($scope.query.sequence);
    };

    /**
     * Load more results.
     */
    $scope.load_more_results = function() {
        $scope.page_size += default_page_size;
        get_results();
    };

    /**
     * Calculate how many items are visible.
     */
    $scope.displayed_items = function() {
        return Math.min($scope.page_size, $scope.count);
    };

});
