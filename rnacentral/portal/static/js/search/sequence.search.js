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
		failed: false
	};
	$scope.results = [];
	$scope.count = 0;

    /**
     * Retrive results given a results url.
     */
	var get_results = function(url) {
		$http({
			url: url,
			method: 'GET'
		}).success(function(data){
			console.log('Results retrieved');
			console.log(data);
			$scope.results = data.results;
		}).error(function(){
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
					$scope.count = data.count;
					console.log('Results ready');
					window.clearInterval(interval);
					// get results
					get_results(data.url);
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
		$http({
			url: '/api/v1/sequence-search/submit?sequence=' + sequence,
			method: 'GET', // todo: switch to POST
		}).success(function(data) {
			console.log(data);
			poll_job_status(data.url);
		}).error(function() {
			// todo
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

});
