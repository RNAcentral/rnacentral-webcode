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

;angular.module('textSearch').controller('ExportResultsCtrl', ['$scope', '$location', '$http', '$interval', '$window', 'routes', function($scope, $location, $http, $interval, $window, routes) {

    $scope.export = {
        query: null,
        job_id: null,
        data_type: null,
        status: null,
        hits: null,
        progress: -1,
        downloadUrl: null,
        ended_at: null,
        enqueued_at: null,
        error_message: '',
        isDownloading: false,
    };
    $scope.routes = routes;

    var interval;

    /**
     * Get status of the export job and return a promise.
     */
     function get_job_status() {
        return $http({
            url: routes.exportApp() + '/download/' + $scope.export.job_id + '/' + $scope.export.data_type,
            method: 'GET'
        }).then(
            function(response) {
                if (response.headers('content-type').includes('application/json')) {
                    $scope.export.hits = response.data.hit_count;

                    // Check progress
                    if ($scope.export.data_type === 'fasta') {
                        $scope.export.progress = (response.data.progress_ids + response.data.progress_fasta) / 2 || 0;
                    } else if ($scope.export.data_type === 'json') {
                        $scope.export.progress = (response.data.progress_ids + response.data.progress_db_data) / 2 || 0;
                    } else {
                        $scope.export.progress = response.data.progress_ids || 0;
                    }

                    // Check status
                    $scope.export.status = response.data.state === 'RUNNING' ? 'running' : response.data.state ? response.data.state : 'pending';
                    if ($scope.export.status === 'FAILURE') {
                        $interval.cancel(interval);
                    }
                } else {
                    $interval.cancel(interval);
                    $scope.export.status = 'finished';
                    $scope.export.progress = 100;

                    // Store the download URL
                    var blob = new Blob([response.data], { type: response.headers('content-type') });
                    $scope.export.downloadUrl = window.URL.createObjectURL(blob);
                }
                update_page_title();
            },
            function(response) {
                if (response.status === 404) {
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
     * Download the file.
     */
    function fetch_file() {
        $scope.export.isDownloading = true;

        return $http({
            url: routes.exportApp() + '/download/' + $scope.export.job_id + '/' + $scope.export.data_type,
            method: 'GET',
            responseType: 'arraybuffer' // Ensure the response is handled as binary for file download
        }).then(
            function(response) {
                var blob = new Blob([response.data], { type: response.headers('content-type') });
                $scope.export.downloadUrl = window.URL.createObjectURL(blob); // Create the download URL
                $scope.downloadFile(); // Trigger the download
                $scope.export.isDownloading = false;
            },
            function(response) {
                $scope.export.error_message = 'Error downloading file';
                $scope.export.isDownloading = false;
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
        var max_interval = 3000;  // 3 seconds

        interval = $interval(function(){
            get_job_status();
        }, max_interval);
    }

    /**
     * Show progress in page title.
     */
    function update_page_title() {
        if ($scope.export.status === 'FAILURE') {
            $window.document.title = 'Export failed';
        } else if ($scope.export.error_message !== '') {
            $window.document.title = 'Results expired';
        } else {
            $window.document.title = Math.round($scope.export.progress) + '% | Exporting results';
        }
    }

    /**
     * Function to handle file download via button.
     */
    $scope.downloadFile = function() {
        if ($scope.export.downloadUrl) {
            var a = document.createElement('a');
            a.style.display = 'none';
            a.href = $scope.export.downloadUrl;
            a.download = $scope.export.job_id + '.' + ($scope.export.data_type === 'json' ? 'json.gz' : $scope.export.data_type === 'fasta' ? 'fasta.gz' : 'txt.gz');
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL($scope.export.downloadUrl);
        }
    };

    /**
     * Fetch the file for download.
     */
    $scope.triggerDownload = function() {
        fetch_file();
    };

    /**
     * Get job id from the url and begin retrieving data.
     */
    function initialize() {
        if ($location.url().indexOf("/export/results?job=") > -1) {
            $scope.export.job_id = $location.search().job;
            $scope.export.data_type = $location.search().data_type;
            get_job_status().then(function(){
                poll_job_status();
            });
        }
    }

    // get job id and start updating the status
    initialize();

}]);
