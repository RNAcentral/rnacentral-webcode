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
 * Angular.js code for exporting metadata search results.
 */

;rnaMetasearch.controller('ExportResultsCtrl', ['$scope', '$location', '$http', '$interval', function($scope, $location, $http, $interval) {

    $scope.export = {
        query: null,
        job_id: null,
        status: null,
        hits: 0,
        progress: -1,
        ended_at: null,
        enqueued_at: null,
        error_message: '',
    };

    var interval;

    /**
     * Get status of the export job.
     */
     function get_job_status() {
        $http({
            url: '/export/job-status?job=' + $scope.export.job_id,
            method: 'GET'
        }).success(function(data) {
            $scope.export = _.extend($scope.export, data);
            $scope.export['expiration'] = new Date($scope.export['expiration']);
            if (data.status === 'finished') {
                $interval.cancel(interval);
            };
        }).error(function(data, status){
            if ( status === 404 ) {
                $scope.export.error_message = 'Job not found';
                $interval.cancel(interval);
            }
        });
     }

    /**
     * Poll the server to get the latest status of the export job.
     */
    function poll_job_status() {
        interval = $interval(function(){
            get_job_status();
        }, 1000);
    }

    /**
     * Get job id from the url and begin retrieving data.
     */
    function initialize () {
       if ($location.url().indexOf("/export/results?job=") > -1) {
            $scope.export.job_id = $location.search().job;
            get_job_status();
            poll_job_status();
       }
    }

    // get job id and start updating the status
    initialize();

}]);
