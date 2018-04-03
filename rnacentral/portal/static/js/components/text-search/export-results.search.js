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

/**
 * Angular.js code for exporting metadata search results.
 */

;angular.module('textSearch').controller('ExportResultsCtrl', ['$scope', '$location', '$http', '$interval', '$window', function($scope, $location, $http, $interval, $window) {

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
     * Get status of the export job and return a promise.
     */
     function get_job_status() {
        return $http({
            url: '/export/job-status?job=' + $scope.export.job_id,
            method: 'GET'
        }).then(
            function(response) {
                $scope.export = _.extend($scope.export, response.data);
                $scope.export.expiration = new Date($scope.export.expiration);
                if (response.data.status === 'finished' || response.data.status === 'failed') {
                    $interval.cancel(interval);
                }
                update_page_title();
            },
            function(response) {
                if ( response.status === 404 ) {
                    $scope.export.error_message = 'Job not found';
                } else {
                    $scope.export.error_message = 'Unknown error';
                }
                $interval.cancel(interval);
                update_page_title();
            }
        );
     }

    /**
     * Format progress for use with ng-style and CSS.
     */
    $scope.get_progress = function() {
        return $scope.export.progress + '%';
    };

    /**
     * Poll the server to get the latest status of the export job.
     * Set polling interval dynamically based on the number of hits.
     */
    function poll_job_status() {
        var min_interval = 1, // 1 second
            max_interval = 3, // 3 seconds
            polling_interval = Math.max(min_interval, Math.min($scope.export.hits / 1000, max_interval)) * 1000;

        interval = $interval(function(){
            get_job_status();
        }, polling_interval);
    }

    /**
     * Show progress in page title.
     */
    function update_page_title() {
        if ($scope.export.status === 'failed') {
            $window.document.title = 'Export failed';
        } else if ($scope.export.error_message !== '') {
            $window.document.title = 'Results expired';
        } else {
            $window.document.title = Math.round($scope.export.progress) + '% | Exporting results';
        }
    }

    /**
     * Get job id from the url and begin retrieving data.
     */
    function initialize() {
       if ($location.url().indexOf("/export/results?job=") > -1) {
            $scope.export.job_id = $location.search().job;
            get_job_status().then(function(){
                poll_job_status();
            });
       }
    }

    // get job id and start updating the status
    initialize();

}]);
