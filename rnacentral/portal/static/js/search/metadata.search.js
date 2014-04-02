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

// RNAcentral metasearch app.

;var rnaMetasearch = angular.module('rnaMetasearch', ['chieffancypants.loadingBar']);

rnaMetasearch.controller('ResultsListCtrl', function($scope, $http) {

	$scope.query = {
					text: 9606,
					failed: false
	               };

    $scope.submit_query = function() {
    	if (!$scope.queryForm.$valid) {
    		$scope.query.failed = true;
    		return;
    	}
    	$scope.query.failed = false;
		$http({
			url: '/api/v1/search',
			method: 'GET',
			params: {taxid: $scope.query.text}
		}).success(function(data) {
			$scope.rnas = data;
		});
    };

});
